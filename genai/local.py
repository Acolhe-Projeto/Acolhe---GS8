"""Read-only local setup diagnostic; never downloads weights or starts a service."""
import argparse
import json
from pathlib import Path
import urllib.request

from genai.service import DEFAULT_MODEL, keep_alive, runtime_options


def check(model=DEFAULT_MODEL, verify_release=False):
    result = {"model": model, "endpoint": "http://127.0.0.1:11434", "ready": False,
              "options": runtime_options(), "keep_alive": keep_alive()}
    try:
        with urllib.request.urlopen(result["endpoint"] + "/api/tags", timeout=5) as response:
            installed = json.loads(response.read())["models"]
        match = next((m for m in installed if m.get("name") == model or m.get("model") == model), None)
        result.update(ready=match is not None, digest=match.get("digest") if match else None)
        if not match:
            result["action"] = "ollama pull " + model
        elif verify_release:
            manifest = json.loads(Path(__file__).with_name("model_manifest.json").read_text(encoding="utf-8"))
            result["expected_digest"] = manifest["ollama_manifest_digest"]
            result["ready"] = model == manifest["model"] and result["digest"] == result["expected_digest"]
            if not result["ready"]:
                result["error"] = "O modelo instalado difere da versao avaliada. Confira genai/model_manifest.json."
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result.update(ready=False, error=str(exc), action="Instale/inicie Ollama local e execute novamente.")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--verify-release", action="store_true", help="Require the exact model digest used in the delivered evaluation")
    args = parser.parse_args()
    status = check(args.model, verify_release=args.verify_release)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    raise SystemExit(0 if status["ready"] else 1)
