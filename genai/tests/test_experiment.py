import json
import os
import contextlib
import io
import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from genai import compare, experiment, local, service
from genai.execute_notebook import llm_notebook


class ExperimentTests(unittest.TestCase):
    def test_cpu_payload_and_explicit_model(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"message": {"content": json.dumps({"answer":"ola", "sources":[]})}}).encode()
        with patch("urllib.request.urlopen", return_value=response) as request:
            service.generate("test", service.DEFAULT_MODEL)
        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(payload["options"]["num_gpu"], 0)
        self.assertEqual(payload["options"]["num_ctx"], 2048)
        self.assertEqual(payload["options"]["num_predict"], 256)
        self.assertEqual(payload["keep_alive"], 0)

    def test_compare_bilingual_context_and_invalid_citation(self):
        with patch.object(compare, "generate", side_effect=[
            {"answer": "Espera.", "sources": []},
            {"answer": "Espera.", "sources": ["made_up"]},
            {"tool": "retrieve", "query": "cruzar calle"},
            {"answer": "Espera.", "sources": ["crossing"]},
        ]) as generate:
            rows = compare.compare("¿Cómo cruzar la calle?", "test", "es")
        self.assertEqual([r["mode"] for r in rows], ["baseline", "rag", "agent"])
        self.assertFalse(rows[1]["citation_ids_valid"])
        self.assertTrue(rows[2]["citation_ids_valid"])
        self.assertIn("en español", generate.call_args_list[1].args[0])
        self.assertIn("acera", generate.call_args_list[1].args[0])
        schema = generate.call_args_list[1].kwargs["schema"]
        self.assertEqual(schema["properties"]["sources"]["items"]["enum"], ["crossing"])

    def test_transport_failure_is_blocked(self):
        with patch.object(compare, "generate", side_effect=OSError("offline")):
            rows = compare.compare("rua", "test")
        self.assertTrue(all(r["status"] == "blocked" for r in rows))

    def test_invalid_plan_is_not_counted_as_safety_refusal(self):
        with patch.object(compare, "generate", return_value=["invalid plan"]):
            rows = compare.compare("rua", "test")
        self.assertEqual(rows[2]["status"], "invalid_output")

    def test_malformed_generation_is_not_counted_as_server_unavailable(self):
        with patch.object(compare, "generate", side_effect=service.InvalidModelOutput("truncated")):
            rows = compare.compare("rua", "test")
        self.assertTrue(all(r["status"] == "invalid_output" for r in rows))

    def test_service_distinguishes_invalid_generation_from_transport(self):
        with patch.dict("os.environ", {"ACOLHE_OLLAMA_MODEL": "test"}):
            with patch.object(service, "generate", side_effect=service.InvalidModelOutput("truncated")):
                result = service.answer("Como atravessar a rua?")
            self.assertEqual(result["reason"], "invalid_llm_output")
            with patch.object(service, "generate", side_effect=OSError("offline")):
                result = service.answer("Como atravessar a rua?")
            self.assertEqual(result["reason"], "llm_unavailable")

    def test_empty_context_schema_forbids_citations(self):
        self.assertEqual(service.answer_schema([])["properties"]["sources"]["maxItems"], 0)

    def test_preflight_failure_does_not_fabricate_results(self):
        with patch.object(experiment, "check", return_value={"ready": False}), patch.object(experiment, "compare") as compare_call:
            report = experiment.run()
        compare_call.assert_not_called()
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["cases"], [])

    def test_each_variant_sees_same_case_and_language(self):
        results = [{"mode": mode, "status": "executed", "schema_valid": True,
                    "citation_ids_valid": None, "seconds": 1.0} for mode in ("baseline", "rag", "agent")]
        with patch.object(experiment, "check", return_value={"ready": True, "digest": "abc"}), patch.object(experiment, "compare", return_value=results) as compare_call:
            report = experiment.run("test", limit=2)
        self.assertEqual(compare_call.call_args_list[1].args, ("¿Cómo cruzar la calle?", "test", "es"))
        self.assertEqual(report["summary"]["rag"]["executed"], 2)
        self.assertEqual(report["model_digest"], "abc")
        self.assertEqual(report["human_review"], "pending")

    def test_local_diagnostic_reports_missing_model(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"models":[]}'
        with patch("urllib.request.urlopen", return_value=response):
            report = local.check()
        self.assertFalse(report["ready"])
        self.assertIn(service.DEFAULT_MODEL, report["action"])

    def test_twenty_cases_include_bilingual_refusals(self):
        rows = experiment.cases()
        self.assertEqual(len(rows), 20)
        self.assertEqual({r["language"] for r in rows if r["expected_refusal"]}, {"pt", "es"})

    def test_notebook_executes_report_reader_without_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps({"status": "partial", "model": "test", "created_at": "test", "summary": {}}), encoding="utf-8")
            notebook = llm_notebook(path)
        output = "".join(notebook["cells"][1]["outputs"][0]["text"])
        self.assertEqual(json.loads(output)["status"], "partial")
        self.assertEqual(notebook["cells"][1]["execution_count"], 1)

    def test_notebook_reader_runs_from_notebooks_directory(self):
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "genai/reports/report.json"
            report.parent.mkdir(parents=True)
            (root / "genai/notebooks").mkdir()
            report.write_text(json.dumps({"status": "completed", "model": "test", "created_at": "test", "summary": {}}), encoding="utf-8")
            try:
                os.chdir(root)
                notebook = llm_notebook(Path("genai/reports/report.json"))
                os.chdir(root / "genai/notebooks")
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec("".join(notebook["cells"][1]["source"]), {})
                self.assertEqual(json.loads(output.getvalue())["status"], "completed")
            finally:
                os.chdir(original)


if __name__ == "__main__":
    unittest.main()
