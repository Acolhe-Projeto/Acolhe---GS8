# GenAI: tutor bilíngue com modelo leve local

## Estado verificado em 16/11/2026

A base já possui corpus autoral PT/ES, recuperação lexical, resposta curada e adaptação Ollama. Esta branch acrescenta perfil CPU, diagnóstico local e comparação reprodutível de baseline/RAG/agente em 20 casos bilíngues. O MVP continua sem dependências Python externas.

Ollama e dois modelos foram executados localmente sem GPU. A escolha final para demonstração supervisionada é **`qwen2.5:1.5b-instruct`**, com 986 MB de pesos Q4_K_M. O modelo 0.5B de 398 MB foi testado primeiro e preservado como experiência histórica; ecoou placeholders/perguntas e falhou em JSON/conteúdo.

Evidências preservadas:

- 0.5B: [20 casos antes](reports/qwen05b-cpu-20261116.json) e [20 casos com JSON Schema](reports/qwen05b-cpu-structured-20261116.json).
- 1.5B: [subconjunto de quatro casos PT/ES](reports/qwen15b-cpu-subset4-20261116.json), mesmas perguntas q01–q04 dos históricos 0.5B. **Não são 20 casos do modelo final.**
- Integração de produto: [smoke 0.5B](reports/service-smoke-20261116.json) e [smoke 1.5B](reports/service-smoke15b-20261116.json), duas perguntas fictícias cada. Com 1.5B, PT mochila passou de eco para resposta substantiva em 5,696 s; ES travessia respondeu com fonte em 6,261 s, com erro ortográfico a revisar.

**Limites de qualidade:** no subconjunto 1.5B, RAG decodificou 4/4 respostas, mas omitiu as fontes nas quatro; agente recusou as quatro perguntas válidas, e baseline teve duas saídas JSON inválidas. O smoke de produto usa outro prompt e devolveu fontes nas duas respostas, por isso a seleção final se limita ao fluxo RAG de demonstração; não demonstra superioridade geral sobre 0.5B. A avaliação humana/pedagógica e benchmark completo do modelo final permanecem pendentes. Os 22 testes automatizados verificam contratos, não certificam qualidade. Veja [análise técnica e comparação](reports/llm_error_analysis.md).

O notebook 02 registra stdout real da leitura do relatório 1.5B com **quatro casos**, executada por Python stdlib. Não repete inferência nem simula treinamento/execução Jupyter.

## Modelo escolhido e limite de hardware

**Qwen2.5 1.5B Instruct**, tag exata `qwen2.5:1.5b-instruct`, digest instalado `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`. O catálogo oficial informa 986 MB de pesos quantizados Q4_K_M, licença Apache-2.0 e suporte PT/ES. Peso em disco não representa RAM total; memória máxima ainda precisa ser medida. Foi executado em CPU i7-8700 nesta máquina de 32 GB RAM. A recomendação de hardware inferior depende de teste, sem promessa de memória/latência universais. Não requer GPU nem fine-tuning.

Fontes primárias: [modelo 1.5B no Ollama](https://ollama.com/library/qwen2.5:1.5b-instruct), [modelo 0.5B histórico](https://ollama.com/library/qwen2.5:0.5b-instruct), [família Qwen2.5](https://qwenlm.github.io/blog/qwen2.5/), [Ollama Windows](https://ollama.com/download/windows).

O perfil fixa `num_gpu=0`, `num_ctx=2048`, `num_predict=256`, temperatura 0, seed 42 e `keep_alive=0`. São limites de recursos, não aprovação de qualidade. Descarregar o modelo após cada chamada poupa residência de RAM e aumenta latência. RAG recupera até três das oito microlições. O Ollama recebe JSON Schema de resposta/plano e enum dos IDs permitidos, conforme a [documentação oficial](https://github.com/ollama/ollama/blob/main/docs/api.md#structured-outputs). O limite de saída ainda pode produzir JSON truncado. Não usamos alias latest, modelos 7B, embeddings, treino ou serviço pago.

## Preparar e executar

Na raiz do repositório, com Python 3.12. Instale/inicie o aplicativo Ollama oficial. Depois:

```powershell
ollama pull qwen2.5:1.5b-instruct
python -B -m genai.local
# Teste curto real (2 perguntas x 3 variantes; agente tem chamada adicional):
python -B -m genai.experiment --limit 2
# Comparação completa; pode demorar em CPU:
python -B -m genai.experiment
```

`genai.local` não instala, inicia ou baixa nada; verifica serviço e tag exata, informa o digest instalado e retorna código 1 quando indisponível. `experiment` interrompe antes da geração se o diagnóstico falhar. Cada execução cria JSON e ficha `.review.md` novos em `genai/reports/`, sem sobrescrever relatórios. `--output caminho-novo.json` permite escolher destino. Só use perguntas e dados fictícios, sem informações pessoais.

Para ativar explicitamente a geração na interface:

```powershell
$env:ACOLHE_OLLAMA_MODEL="qwen2.5:1.5b-instruct"
python -B -m app.server
```

Sem essa variável a interface preserva `retrieval_only`. Uma falha no modelo retorna recusa explícita, nunca texto simulado apresentado como geração. O cliente usa apenas `127.0.0.1:11434`; não há fallback para nuvem. Para teste individual:

```powershell
python -B -m genai.compare --language es --question "¿Cómo cruzar la calle?"
python -B -m unittest discover -s genai/tests -v
python -B -m genai.evaluate
python -B -m genai.execute_notebook
# Atualizar notebook 02 a partir de um relatório real já executado:
python -B -m genai.execute_notebook --llm-report genai/reports/qwen15b-cpu-subset4-20261116.json
```

## Contrato e avaliação

`answer(question, language="pt")` aceita `pt`/`es` e devolve `answer`, `sources`, `mode`:

- `retrieval_only`: texto autoral recuperado; nenhum LLM.
- `local_llm_rag`: JSON do Ollama com IDs restritos aos trechos recuperados.
- `refusal`: proteção de entrada, ausência de conteúdo, indisponibilidade ou saída inválida.

O experimento usa as mesmas perguntas, idioma, modelo e parâmetros nas três variantes: baseline sem contexto, RAG lexical e agente com ferramenta `retrieve`/`refuse`. Não é o endpoint infantil nem contorna seus filtros. Registra resposta bruta, IDs de contexto, rastro do agente, latência total por variante (incluindo recarga), versão Python, SHA-256 do corpus e digest do modelo quando disponível. Um plano malformado é `invalid_output`, não uma recusa correta. `blocked` indica bloqueio de infraestrutura ou envelope de serviço. Saída do modelo que não decodifica é `invalid_output`. `status=completed` significa que o executor percorreu os casos sem bloqueio de infraestrutura; não significa qualidade aprovada. Pode coexistir com planos inválidos, JSON/schema inválido, referências incorretas e respostas factualmente erradas: consultar contagens e respostas por caso.

As métricas automáticas são contagens de execução, JSON/schema e IDs de citação válidos; **não medem correção, factualidade ou qualidade pedagógica**. A ficha exige revisão humana de correção, suporte por fonte, idioma e recusa. Examinar pelo menos cinco erros reais com trecho, causa, mitigação e reteste; se não houver cinco, ampliar o conjunto sem inventar. As 16 perguntas históricas mais quatro negativas são manuais e pequenas, sem generalização estatística; registrar se `--limit` foi usado. Ajustes posteriores ao corpus exigem novos casos de teste independentes.

## Próximas entregas

Consulte [plano/PRD GenAI](PLAN.md). Foram concluídas duas comparações completas 0.5B, um subconjunto de quatro casos 1.5B, os smokes e análise técnica. Faltam avaliar os 20 casos no modelo final 1.5B, melhorar fontes/roteamento no experimento, revisar idioma/qualidade com humanos e medir memória máxima. O relatório histórico `reports/error_analysis.md` trata erros de recuperação, não de LLM.

Corpus: oito microlições autorais PT/ES, CC-BY-4.0, revisão pedagógica pendente. Filtros de termos e IDs válidos não impedem toda alucinação/injeção. Os dois modelos testados falharam em partes do experimento. O 1.5B respondeu melhor à pergunta PT no smoke, mas ainda errou idioma e roteamento/fontes; não está aprovado para crianças. O sistema não decide travessias nem substitui responsável. Para crianças reais, corpus/respostas e privacidade exigem validação humana própria; o protótipo usa adultos e dados fictícios.
