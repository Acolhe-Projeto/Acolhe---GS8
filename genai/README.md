# GenAI

Assistente local em PT/ES com Qwen2.5 3B Q4_K_M, recuperação lexical e agente de consulta/recusa. A interface usa RAG. O modelo tem 3,09 bilhões de parâmetros e aproximadamente 1,9 GB de pesos; a especialização não alterou seus pesos.

## Usar

Siga a instalação do README da raiz. scripts/preparar-demo.ps1 baixa a LLM pelo Ollama; scripts/iniciar-demo.ps1 confere o mesmo digest usado na avaliação. O corpus, os prompts, as guardas e o agente estão no código.

O [relatório GenAI](../docs/entregas/GENAI_RELATORIO.md) apresenta método, resultados e erros. No D16, baseline acertou 7/16 e RAG/agente, 14/16, em revisão técnica exploratória. A revisão humana permanece pendente.

## Arquivos

- data/corpus.json: fonte canônica das oito microlições PT/ES.
- model_manifest.json: identidade, tamanho, licença e digest do modelo.
- service.py e compare.py: recuperação, geração e agente.
- avaliacao: casos, limiar, respostas, rastros e revisão técnica.
- notebooks: recuperação, comparação da LLM e integração HTTP.

## Reproduzir a avaliação

Com Ollama aberto e a LLM instalada, executar na raiz:

```powershell
.\.venv\Scripts\python.exe -m genai.local --verify-release
$env:ACOLHE_OLLAMA_NUM_GPU = '-1'
$env:ACOLHE_OLLAMA_KEEP_ALIVE = '2m'
.\.venv\Scripts\python.exe -m genai.experiment --dataset genai/avaliacao/teste_dev.json --output genai/reports/nova-avaliacao-dev.json
```

O destino deve ser novo; a rotina não sobrescreve evidências. Para repetir o D16, usar teste_independente_D.json e outro destino. Ele já foi examinado e não constitui um novo teste independente. O processo também gera uma ficha local opcional para revisão humana.

O manifesto identifica a licença Qwen Research. A licença declarada do corpus autoral é CC BY 4.0.
