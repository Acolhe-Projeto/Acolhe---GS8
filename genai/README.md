# GenAI — mobilidade educativa PT/ES

Modelo final **qwen2.5:3b-instruct**, Q4_K_M, 3,09B parâmetros (~1,9 GB de pesos), dentro do limite de 4B solicitado. Ollama 0.40.16; a comparação final confirmou 2.085.963.693 bytes em VRAM na RX 6750 XT. Licença Qwen Research: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE. Peso em disco não é memória total.

O [relatório formal](../docs/entregas/GENAI_RELATORIO.md) reúne tarefa, equipe, diagramas, fontes, placar, erros e limitações. [Checklist oficial](../docs/ENTREGA_CHECKLIST.md). Os históricos 0.5B/1.5B e CPU permanecem identificados; não são o perfil final GPU.

Para abrir os dois módulos e gravar em cerca de90segundos, use o [guia rápido](../docs/entregas/COMO_USAR_E_GRAVAR.md) e scripts/iniciar-demo.ps1. As três perguntas do roteiro foram verificadas por HTTP real em docs/evidencias/roteiro-http-real.json.

## Executar na raiz

Instale Python 3.12 e Ollama. O servidor e GenAI usam biblioteca padrão; dependências de Vision são opcionais para GenAI.

```powershell
ollama pull qwen2.5:3b-instruct
$env:ACOLHE_OLLAMA_MODEL="qwen2.5:3b-instruct"
$env:ACOLHE_OLLAMA_NUM_GPU="-1"
$env:ACOLHE_OLLAMA_KEEP_ALIVE="2m"
python -B -m genai.local
python -B -m app.server
```

Abra http://127.0.0.1:8080. CPU: use NUM_GPU=0. A configuração padrão é CPU e unload=0; GPU e residência 2m são explícitas. Confirme size_vram em /api/ps: pedir offload sozinho não comprova GPU. Sem MODEL, a interface usa texto curado retrieval_only; falhas do modelo geram recusa explícita. Não há fallback para nuvem.

## Reproduzir avaliação

```powershell
python -B -m genai.evaluate
python -B -m genai.experiment --dataset genai/avaliacao/teste_dev.json
python -B -m genai.experiment --dataset genai/avaliacao/teste_independente_C.json
python -B -m unittest discover -s genai/tests -v
python -B -m genai.execute_notebook
python -B -m genai.execute_notebook --llm-report genai/avaliacao/qwen3b-v4-gpu-dev20.json
```

Cada comparação grava novo JSON/ficha humana sem sobrescrever evidências. Temperatura 0, seed 42, contexto 2048, saída 256. O conjunto dev20 guiou ajustes; holdoutC12 foi congelado antes de v4. Baseline, RAG e agente recebem as mesmas perguntas/modelo. Agente toma decisão LLM retrieve/refuse com ferramenta e rastro; não é LoRA nem treinamento de pesos.

## Evidência e limites

- [Dev20 GPU](avaliacao/qwen3b-v4-gpu-dev20.json) e [holdoutC12 GPU](avaliacao/qwen3b-v4-gpu-holdout12.json): contratos válidos em todas as variantes. Recall@1/@3 no desenvolvimento: 16/16; limiar 2.0 justificado em avaliacao/limiar.json.
- [Revisão técnica exploratória pelo agente](avaliacao/revisao_tecnica_v4.json): dev baseline 5/20, RAG 16/20, agente 16/20; C12: 4/12, 8/12, 9/12. Não é julgamento humano cego. Fontes/JSON válidos não provam correção.
- O notebook01 executa recuperação; 02 lê relatório real; 03 registra HTTP real PT/ES e recusa. Outputs executados por Python stdlib, sem alegar kernel Jupyter ou treino inexistente.
- Oito microlições autorais, CC-BY-4.0, revisão pedagógica pendente. Fonte canônica data/corpus.json e snapshot atribuído em base/.
- POST /api/assistant responde answer/sources/mode/model. O aviso fixo de travessia é política curada visível, separado da resposta LLM e não usado para inflar o placar congelado.

Persistem falhas de idioma, intenção, omissão e falsa recusa. Guardas não garantem segurança universal. Uso com adultos e perguntas fictícias; não decide travessias. Faltam revisão humana, gravação/publicação do vídeo e envio no Teams. Veja o [roteiro](../docs/entregas/ROTEIRO_VIDEOS.md).
