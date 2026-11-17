"""Real local LLM only. Never writes fabricated baseline/RAG/agent scores."""
import argparse
import json
import time
from genai.service import DEFAULT_MODEL, InvalidModelOutput, answer_schema, generate, retrieve, validate_output, grounded_prompt, input_guard, refusal, unsafe_output, missing_detail

TOOL_SCHEMA = {"type": "object", "properties": {"tool": {"type": "string", "enum": ["retrieve", "refuse"]},
               "query": {"type": "string", "maxLength": 160}}, "required": ["tool", "query"], "additionalProperties": False}

def compare(question, model, language="pt"):
    if language not in ("pt", "es"):
        raise ValueError("language must be pt or es")
    results = []
    for mode in ("baseline", "rag", "agent"):
        start = time.perf_counter()
        context = []
        trace = []
        generations = []
        if input_guard(question) or missing_detail(question):
            reason = "safety_guard" if input_guard(question) else "missing_detail"
            results.append({"mode": mode, "status": "refused", "refusal_origin": reason, "output": refusal(language, reason), "trace": trace, "generations": generations, "seconds": round(time.perf_counter()-start, 3)})
            continue
        try:
            if mode == "rag":
                context = retrieve(question, k=1)
            elif mode == "agent":
                plan_prompt = ("Select a tool. retrieve searches the local educational material about road crossing, buses, "
                               "getting help when lost, greetings and Portuguese/Spanish vocabulary. Use retrieve for ALL questions "
                               "about those topics, even if uncertain; the search tool will check if material exists. "
                               "Use refuse only for unrelated topics (finance, medicine, secrets). Do not answer the question. "
                               "Return tool and a short search query in the question's language. "
                               'Examples: Estou perdido -> retrieve; Como atravessar a rua? -> retrieve; silla -> retrieve; '
                               'Comprar ações -> refuse. Question: ' + json.dumps(question, ensure_ascii=False))
                plan = generate(plan_prompt, model, schema=TOOL_SCHEMA, trace=generations)
                trace.append({"decision": plan})
                if not isinstance(plan, dict) or plan.get("tool") != "retrieve" or not isinstance(plan.get("query"), str):
                    status = "refused" if isinstance(plan, dict) and plan.get("tool") == "refuse" else "invalid_output"
                    results.append({"mode": mode, "status": status, "refusal_origin": "model_plan" if status == "refused" else None,
                                    "output": refusal(language) if status == "refused" else None, "trace": trace, "generations": generations, "seconds": round(time.perf_counter()-start, 3)})
                    continue
                # Keep the user's original language when a small planner translates its query.
                search_query = question + " " + plan["query"][:160]
                context = retrieve(search_query, k=1)
                trace.append({"tool": "retrieve", "requested_query": plan["query"], "executed_query": search_query, "ids": [d["id"] for d in context]})
            if mode != "baseline" and not context:
                results.append({"mode": mode, "status": "refused", "refusal_origin": "retrieval_no_evidence", "output": refusal(language), "trace": trace, "generations": generations, "context_ids": [], "seconds": round(time.perf_counter()-start, 3)})
                continue
            if context:
                prompt = grounded_prompt(question, language, context)
            else:
                prompt = ("Responda em português em até 240 caracteres. O domínio é vocabulário português/espanhol e mobilidade educativa. "
                           "Para outros temas, diga que não consta. Nunca autorize crianças a sair ou atravessar sem adulto. "
                           "Não peça dados pessoais. Retorne JSON answer e sources (lista vazia porque não recebeu documentos). Pergunta: " if language == "pt" else
                          "Responde en español hasta 240 caracteres. El tema es vocabulario portugués/español y movilidad educativa. "
                          "Para otros temas di No consta en el material. Nunca autorices a niños a salir o cruzar sin adulto. "
                          "No pidas datos personales. Devuelve JSON con answer y sources (lista vacía porque no recibiste documentos). Pregunta: ")
                prompt += json.dumps(question, ensure_ascii=False)
            result = generate(prompt, model, schema=answer_schema([d["id"] for d in context]), trace=generations)
            schema_valid = (isinstance(result, dict) and isinstance(result.get("answer"), str)
                            and 0 < len(result["answer"].strip()) <= 240
                            and isinstance(result.get("sources"), list)
                            and all(isinstance(s, str) for s in result["sources"]))
            grounded = validate_output(result, [d["id"] for d in context]) if context else None
            results.append({"mode": mode, "status": "executed", "output": result, "trace": trace,
                            "context_ids": [d["id"] for d in context], "schema_valid": schema_valid,
                            "citation_ids_valid": grounded, "unsafe_output": unsafe_output(result.get("answer", "")) if isinstance(result, dict) else True, "generations": generations, "seconds": round(time.perf_counter()-start, 3)})
        except InvalidModelOutput as exc:
            results.append({"mode": mode, "status": "invalid_output", "error": str(exc), "trace": trace, "generations": generations,
                            "seconds": round(time.perf_counter()-start, 3)})
        except (OSError, ValueError, KeyError, RuntimeError) as exc:
            results.append({"mode": mode, "status": "blocked", "error": str(exc), "trace": trace, "generations": generations,
                            "seconds": round(time.perf_counter()-start, 3)})
    return results

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--question", default="Como atravessar a rua?")
    p.add_argument("--language", choices=("pt", "es"), default="pt")
    a = p.parse_args()
    print(json.dumps(compare(a.question, a.model, a.language), ensure_ascii=False, indent=2))
