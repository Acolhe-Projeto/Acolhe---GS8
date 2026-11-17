"""Execute our small standard-library notebook cells and capture actual stdout (no fake outputs)."""
import contextlib
import argparse
import io
import json
from pathlib import Path


def llm_notebook(report_path):
    """Execute report-reading code, not the inference again; capture real stdout."""
    code = ("import json\nfrom pathlib import Path\n"
            + "report_path = Path(" + repr(Path(report_path).as_posix()) + ")\n"
            + "if not report_path.is_absolute():\n"
              "    for base in (Path.cwd(), *Path.cwd().parents):\n"
              "        candidate = base / report_path\n"
              "        if candidate.is_file():\n"
              "            report_path = candidate\n"
              "            break\n"
              "report = json.loads(report_path.read_text(encoding='utf-8'))\n"
            + "print(json.dumps({'status': report['status'], 'model': report['model'], "
              "'created_at': report['created_at'], 'case_count': len(report.get('cases', [])), "
              "'summary': report.get('summary', {})}, ensure_ascii=False, indent=2))\n")
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(code, "<llm-report-cell>", "exec"), {})
    return {"cells": [
        {"cell_type": "markdown", "metadata": {}, "source": [
            "# Comparação local real — baseline, RAG e agente\n",
            "Inferências foram executadas por genai.experiment; o perfil CPU/GPU e as evidências constam do JSON. Esta célula foi executada por Python stdlib (compile/exec), sem kernel Jupyter, e lê o relatório salvo. Não repete inferência e não executa treinamento.\n",
            "Consulte o JSON e o relatório GenAI para análise técnica. Avaliação humana permanece pendente. completed não significa qualidade aprovada.\n"]},
        {"cell_type": "code", "execution_count": 1, "metadata": {}, "source": code.splitlines(True),
         "outputs": [{"output_type": "stream", "name": "stdout", "text": output.getvalue().splitlines(True)}]}],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "acolhe_executor": "Python stdlib compile/exec; read saved real inference report"},
        "nbformat": 4, "nbformat_minor": 5}

def run():
    source = [
        "import json\nfrom genai.evaluate import evaluate\nreport = evaluate()\nprint(json.dumps(report, ensure_ascii=False, indent=2))",
        "import os\nfrom genai.service import answer\n"
        "configured_model = os.environ.pop('ACOLHE_OLLAMA_MODEL', None)\n"
        "try:\n    print(json.dumps(answer('Como atravessar a rua?', 'pt'), ensure_ascii=False, indent=2))\n"
        "finally:\n    if configured_model is not None:\n        os.environ['ACOLHE_OLLAMA_MODEL'] = configured_model\n"
    ]
    cells = [{"cell_type":"markdown","metadata":{},"source":["# Avaliação real da recuperação\nExecutado com Python stdlib. Não executa LLM."]}]
    namespace = {}
    for i, code in enumerate(source, 1):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(code, "<notebook-cell>", "exec"), namespace)
        cells.append({"cell_type":"code","execution_count":i,"metadata":{},"source":code.splitlines(True),"outputs":[{"output_type":"stream","name":"stdout","text":output.getvalue().splitlines(True)}]})
    root=Path(__file__).parent
    (root/"notebooks").mkdir(exist_ok=True)
    notebook={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},"nbformat":4,"nbformat_minor":5}
    (root/"notebooks/01_retrieval.ipynb").write_text(json.dumps(notebook,ensure_ascii=False,indent=2),encoding="utf-8")
    (root/"reports").mkdir(exist_ok=True)
    report=namespace["report"]
    (root/"reports/retrieval.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"recall_at_1":report["recall_at_1"],"recall_at_3":report["recall_at_3"],"errors":len(report["errors"])}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm-report", type=Path, help="render real saved inference report into notebook 02")
    args = parser.parse_args()
    if args.llm_report:
        notebook = llm_notebook(args.llm_report)
        (Path(__file__).parent / "notebooks/02_local_llm.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        run()
