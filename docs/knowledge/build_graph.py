"""Rebuild a local Graphify map; preserve reviewed semantic annotations separately.

Run with the Python environment containing graphifyy[pdf,sql,terraform].
No model API, API key, watcher, hook or remote backend is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from collections import Counter

from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.detect import detect
from graphify.diagnostics import diagnose_extraction
from graphify.export import to_json
from graphify.extract import extract
from graphify.report import generate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "graphify-out"
KNOWLEDGE = ROOT / "docs" / "knowledge"


def ident(path):
    return re.sub(r"[^\w]+", "_", Path(path).with_suffix("").as_posix().casefold()).strip("_")


def text(path):
    if path.suffix == ".pdf":
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return path.read_text(encoding="utf-8-sig")


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def build(force=False):
    OUT.mkdir(exist_ok=True)
    detection = detect(ROOT)
    # Generated knowledge, vendored dependencies and runtime outputs are never inputs.
    def allowed(value):
        rel = Path(value).relative_to(ROOT).as_posix()
        return not rel.startswith(("graphify-out/", "docs/knowledge/", ".venv/"))
    for category, files in detection["files"].items():
        detection["files"][category] = [p for p in files if allowed(p)]
    detection["total_files"] = sum(map(len, detection["files"].values()))
    detection["total_words"] = sum(len(text(Path(p)).split()) for category in ("code", "document", "paper") for p in detection["files"][category])
    detection["warning"] = f"Corpus: {detection['total_files']} supported source files, approximately {detection['total_words']:,} words; generated knowledge outputs excluded."
    code_files = [Path(p) for p in detection["files"]["code"]]
    ast = extract(code_files, root=ROOT, cache_root=ROOT, parallel=False)
    ast_sources = {n.get("source_file") for n in ast["nodes"]}
    unmodeled_code = [p for p in code_files if p.relative_to(ROOT).as_posix() not in ast_sources]
    semantic = json.loads((KNOWLEDGE / "semantic.json").read_text(encoding="utf-8"))
    # Reusing human/agent annotations after their source changes would falsely certify
    # coverage. Keep historical annotations out until reviewed at their new hash.
    stale = []
    verified = set()
    for rel, record in semantic["coverage"].items():
        path = ROOT / rel
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]:
            verified.add(rel)
        else:
            stale.append(rel)
    nodes = list(ast["nodes"])
    edges = list(ast["edges"])
    known = {n["id"] for n in nodes}
    for node in semantic["nodes"]:
        if node["source_file"] in verified and node["id"] not in known:
            nodes.append(dict(node, _origin="semantic"))
            known.add(node["id"])
    for edge in semantic["edges"]:
        if edge["source_file"] in verified and edge["source"] in known and edge["target"] in known:
            edges.append(dict(edge, _origin="semantic"))

    # Literal section headings, inline paths and links supplement reviewed concepts.
    # This is structural indexing, not a claim that an LLM reviewed new prose.
    content_files = [Path(p) for cat in ("document", "paper") for p in detection["files"][cat]] + unmodeled_code
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    supplements = [ROOT / p for p in tracked if (ROOT / p).is_file()
                   and p not in {str(Path(f).relative_to(ROOT).as_posix()) for fs in detection["files"].values() for f in fs}]
    content_files += [p for p in supplements if p.suffix in {".ipynb", ".ino", ".bpmn", ".css", ".csv", ".example", ".cmd", ".webmanifest"} or "Dockerfile" in p.name or p.name.startswith(".")]
    structural_coverage = {}
    for path in content_files:
        if not allowed(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        raw = text(path)
        structural_coverage[rel] = {"lines": len(raw.splitlines()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        node_id = ident(rel) + "_document"
        if node_id not in known:
            nodes.append({"id": node_id, "label": rel, "file_type": "paper" if path.suffix == ".pdf" else "document", "source_file": rel, "source_location": "L1" if path.suffix != ".pdf" else "pages 1-10", "_origin": "semantic", "extraction_method": "literal_structure"})
            known.add(node_id)
        for number, line in enumerate(raw.splitlines(), 1):
            heading = re.match(r"^#{1,6}\s+(.+)", line)
            if heading:
                label = heading.group(1).strip()
                section_id = ident(rel) + "_" + re.sub(r"[^\w]+", "_", label.casefold()).strip("_")
                if section_id not in known:
                    nodes.append({"id": section_id, "label": label, "file_type": "concept", "source_file": rel, "source_location": f"L{number}", "_origin": "semantic", "extraction_method": "literal_heading"})
                    known.add(section_id)
                    edges.append({"source": node_id, "target": section_id, "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": rel, "source_location": f"L{number}", "weight": 1.0, "_origin": "semantic"})
        for match in re.finditer(r"`([^`\n]+\.(?:py|js|json|md|yaml|yml|tf|sql|ipynb))`|\[[^\]]+\]\(([^)]+)\)", raw):
            ref = (match.group(1) or match.group(2)).split("#")[0]
            candidate = (path.parent / ref).resolve()
            if not candidate.is_file():
                candidate = (ROOT / ref).resolve()
            if candidate.is_file() and candidate.is_relative_to(ROOT):
                target_rel = candidate.relative_to(ROOT).as_posix()
                target = ident(target_rel)
                if target not in known:
                    target += "_document"
                if target in known and target != node_id:
                    edges.append({"source": node_id, "target": target, "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": rel, "source_location": f"L{raw[:match.start()].count(chr(10))+1}", "weight": 1.0, "_origin": "semantic"})
    for edge in edges:
        edge.setdefault("confidence_score", 1.0 if edge.get("confidence") == "EXTRACTED" else 0.75)
    assert len(known) == len(nodes), "Duplicate node IDs would silently discard evidence"
    assert all(e.get("source") and e.get("target") for e in edges), "Missing edge endpoint"
    extraction = {"nodes": nodes, "edges": edges, "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    G = build_from_json(extraction, root=str(ROOT), directed=False)
    if not G.number_of_nodes():
        raise RuntimeError("Empty graph; refusing publication")
    communities = cluster(G)
    cohesion = score_all(G, communities)
    area_names = {"app": "Aplicação e interface", "genai": "Tutor e avaliação GenAI", "vision": "Objetos e treinamento Vision", "big_data": "Engenharia de dados", "robot": "Robô e segurança", "rpa": "Relatórios e automação", "devsecops": "Infraestrutura e observabilidade", "docs": "Documentação e evidências", "tests": "Contratos e regressões", ".github": "Pipeline de integração", "bi": "Indicadores e negócio"}
    labels = {}
    for cid, members in communities.items():
        areas = Counter(Path(G.nodes[n].get("source_file", "")).parts[0] for n in members if Path(G.nodes[n].get("source_file", "")).parts)
        area = areas.most_common(1)[0][0] if areas else "docs"
        labels[cid] = area_names.get(area, "Configuração do projeto") + f" {cid}"
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not to_json(G, communities, str(OUT / "graph.json"), force=force, built_at_commit=commit, community_labels=labels):
        raise RuntimeError("Graphify shrink guard refused this rebuild; review deletions before --force")
    gods, surprises = god_nodes(G), surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    report = generate(G, communities, cohesion, labels, gods, surprises, detection, {"input": 0, "output": 0}, str(ROOT), suggested_questions=questions, built_at_commit=commit, obsidian=True)
    report = report.replace("0 input", "not metered input").replace("0 output", "not metered output")
    report += "\n\n## Cobertura e custo honestos\n\nAST local + anotações semânticas revisadas pela sessão; headings e referências literais complementam documentos. Contagens de tokens da sessão não estão expostas pela ferramenta: os zeros internos são placeholders e não significam custo zero. Não houve chamada de API de modelo externo. `docs/knowledge/coverage.json` distingue revisão semântica de indexação estrutural.\n\n`graphify-out/` é saída local na árvore Git; escolha explicitamente quais artefatos compartilhar. O mapa descreve código e documentação, não comprova execução de modelos, infraestrutura ou requisitos acadêmicos.\n"
    health = diagnose_extraction(extraction, directed=False, root=str(ROOT))
    report += (f"\n### Alerta de integridade do extrator\n\nGraphify relatou {health['dangling_endpoint_edges']} referências a endpoints não declarados na extração e {health['undirected_same_endpoint_collapsed_edges']} relações colapsadas por par na projeção não direcionada (em especial chaves YAML repetidas). Referências externas e resolução AST têm limites; o mapa pode ser incompleto. A extração bruta permanece em `.graphify_extract.json`; não use ausência de aresta como prova de ausência de dependência.\n")
    if stale:
        report += "\nAnotações semânticas pendentes de revisão após alteração da fonte: " + ", ".join(stale) + ". Foram excluídas deste build; headings ainda indexados.\n"
    (OUT / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    dump(OUT / ".graphify_labels.json", {str(k): v for k, v in labels.items()})
    dump(OUT / ".graphify_extract.json", extraction)
    dump(OUT / ".graphify_detect.json", detection)
    dump(OUT / ".graphify_analysis.json", {"communities": communities, "cohesion": cohesion, "gods": gods, "surprises": surprises, "questions": questions})
    code_hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in code_files}
    dump(KNOWLEDGE / "coverage.json", {"base_commit": commit, "worktree_snapshot": True, "code_files": len(code_files), "code_source_hashes": code_hashes, "ast_nodes": len(ast["nodes"]), "ast_edges": len(ast["edges"]), "unmodeled_code": [p.relative_to(ROOT).as_posix() for p in unmodeled_code], "reviewed_semantic_sources": sorted(verified), "stale_semantic_sources": stale, "structural_sources": structural_coverage, "token_usage": None, "token_usage_reason": "Host agent usage not exposed", "graph_nodes": G.number_of_nodes(), "graph_edges": G.number_of_edges(), "communities": len(communities), "health": health})
    (OUT / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (OUT / ".graphify_root").write_text(str(ROOT), encoding="utf-8")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities; stale semantic sources: {len(stale)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="permit intentional graph shrink")
    build(parser.parse_args().force)
