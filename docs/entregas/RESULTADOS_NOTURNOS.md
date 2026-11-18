# Fechamento dos experimentos noturnos — 17/11/2026

Este documento preserva o resultado GenAI v6/D16 e a rodada noturna histórica de Vision. O Vision ativo foi atualizado depois para YOLO26m: treino com 91 fotos, inferência 960/confiança 0,25; o candidato com 117 fotos não foi promovido. Na validação ampliada, P72,7%/R71,5%; no teste básico reservado de 13 fotos, P71,2%/R72,2%. A meta foi observada nesse lote pequeno, sem comprovar generalização. Fonte atual: [VISION_FINETUNING.md](VISION_FINETUNING.md).

## GenAI

Perfil ativo: Qwen2.5 3B Instruct Q4, protocolo `chat_guidance_v6`, corpus v3. Mantidos oito documentos e 16 campos bilíngues; as 16 visões de orientação não são novas fontes. Intenção de tradução respeita o idioma solicitado; perguntas de orientação recebem texto monolíngue. Preços ausentes são recusados pelo programa, igualmente nas três configurações. Avisos fixos de travessia e pessoa perdida aparecem separados da resposta do modelo.

O desenvolvimento de 20 casos foi usado para escolher o perfil. RAG e agente obtiveram contrato válido em 20/20, fonte esperada em 16/16 positivos e recusa compatível em 20/20. Isso não prova correção semântica. Recuperação dev: recall@1 e @3 = 16/16; limiar 2 reavaliado no corpus v3. O relatório anterior permanece em limiar-corpus-v2.json.

D16 foi congelado antes dos ajustes; v6 escolhido antes de ler o resultado. Os testes são autorais e pequenos, não um benchmark externo. Revisão técnica exploratória pelo agente, com revisão humana pendente:

| Configuração | v4 respostas corretas / 16 | v6 respostas corretas / 16 |
|---|---:|---:|
| Baseline sem contexto | 7 | 7 |
| RAG | 6 | 14 |
| Agente com recuperação | 6 | 14 |

Em v6, RAG/agente citaram a fonte esperada em 8/10 positivos, recusaram corretamente os seis negativos e cumpriram o contrato em 16/16. As duas falhas continuam: d02 recupera ônibus em vez de ajuda a pessoa perdida; d08 recupera garrafa em vez de cadeira. Não ajustamos o sistema após examinar D16. O agente não superou RAG e demora mais nesta execução; a interface continua usando RAG.

### Erros reais e correções verificadas

| Caso | Falha anterior | Medida feita com desenvolvimento | Reteste D16 |
|---|---|---|---|
| d01 RAG | Só dizia usar a faixa, omitindo adulto | Orientação completa no contexto | Inclui adulto e nunca atravessar sozinho |
| d03 RAG | Só traduzia ônibus | Tradução apenas quando solicitada | Espera longe da borda, embarque com responsável |
| d04 RAG | Inventava sentar confortavelmente | Visões monolíngues dos fatos | Espera e embarque conforme fonte |
| d05 RAG | Respondia cadeira em vez de silla | Idioma alvo explícito | silla |
| d06 RAG | Respondia botella em vez de garrafa | Idioma alvo explícito | garrafa |
| d11 RAG | Traduzia ônibus diante de pergunta de preço | Guarda de informação ausente | Recusa; melhoria do programa, não da LLM |

Evidências em genai/avaliacao: qwen3b-v4-D16-night.json, qwen3b-v6-D16-night.json, D16-revisao-tecnica.json, v6-frozen-before-D.json e qwen3b-v6-final-dev20.json. Respostas brutas preservadas. Comparação combina prompt, guarda e forma de apresentar a fonte; não isola causalmente um único fator. Nenhuma alegação de revisão pedagógica concluída.

## Vision — registro histórico anterior ao YOLO26m

Quatro experimentos adicionais concluídos usando apenas as 25 imagens de treino já aprovadas. Nenhuma das 23 fotos de teste foi incorporada ao treino nem usada nesta decisão.

| Experimento | Precisão na validação | Recall na validação | F1 |
|---|---:|---:|---:|
| YOLO26n congelando 10 camadas, 640, 120 épocas | 52,5% | 43,8% | 47,7% |
| YOLO26n congelando 22 camadas, 640, 120 épocas | 48,8% | 43,8% | 46,2% |
| YOLO26n congelando 10 camadas, 960, 100 épocas | 57.7% | 31.2% | 40,5% |
| YOLOv8n congelando 10 camadas, 640, 100 épocas | 48,8% | 41,7% | 44,9% |

Preservado o YOLO26n anterior em produção local: validação P62,1% / R37,5% / F146,8%. A melhoria de apenas um ponto de F1 do melhor candidato vem com perda de precisão e não demonstra vantagem prática em oito imagens. O critério automático sugere um candidato; a revisão não autoriza sua promoção. Manifesto ativo e PDF continuam descrevendo o mesmo modelo, confiança 0,15 e imagem 640.

No conjunto já exposto de 23 imagens, o modelo ativo mantém P60,7% / R51,5%, 34 acertos, 22 falsos positivos e 32 objetos perdidos. É regressão diagnóstica, não teste cego novo. A meta conjunta 70%/70% permanece NÃO atingida. Mais treino nessa amostra não resolveu a falta de variedade. Próximo ganho exige ampliar e revisar o treino e reservar novo teste sem exposição; isso continua pendente, sem inventar resultados.

Decisão e hashes: vision/reports/overnight-decision.json; quatro relatórios night-*.json preservam as grades de validação. Treinos em CPU; GPU AMD não foi prometida para o stack de Vision instalado.

## Uso e validação da rodada histórica

Guia: docs/entregas/TESTAR_AMANHA.md. As fotos de ensaio permanecem locais em docs/qa/testar. Evidência HTTP real da versão atual: docs/evidencias/demo-overnight-http.json. A primeira resposta pode demorar para carregar o modelo. O protótipo pode errar; não usar detecção para decidir travessias.
