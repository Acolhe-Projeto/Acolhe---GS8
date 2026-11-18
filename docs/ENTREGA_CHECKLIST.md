# Checklist atual — GenAI e Vision

Atualizado em 17/11/2026, branch feat/genai-vision. Implementação, execução, qualidade e submissão são estados diferentes; este documento não concede nota.

## Fonte oficial e prazo

Desafio FIAP GS CitizenTech 4ES, 60 páginas, SHA256 236c35530bc23f3f6c48211f022862ff5d1458f17ad2d813e1f9d5130b696c87. Páginas 24, 29–31 e 44 conferidas. Prazo do PDF: 19/11 às 23h55, no Teams de cada disciplina, por um integrante; links públicos funcionando na correção. Conferir o horário no ambiente FIAP.

## GenAI — página 30

| ID | Peso | Critério | Estado |
|---|---:|---|---|
| G01 |0,5| Tarefa e gabarito com não consta | Implementados; dev20 e casos congelados, incluindo D16 |
| G02 |1,0| Base em trechos com fonte | Oito documentos bilíngues, corpus v3; revisão pedagógica pendente |
| G03 |1,0| Recall@1/@3 e limiar | 16/16 no desenvolvimento; limiar 2,0 reavaliado; não é acurácia da resposta |
| G04 |2,0| JSON, fontes e recusa | LLM Qwen3B local e API/UI reais; guardas e falhas semânticas documentadas |
| G05 |2,0| LoRA ou agente versus RAG | Agente retrieve/refuse real comparado; não há LoRA nem pesos treinados pela equipe |
| G06 |2,0| Placar interpretado de três configurações | D16: 7/16 baseline, 14/16 RAG e agente, na revisão técnica exploratória |
| G07 |1,0| Cinco erros e correções | Casos reais e respostas brutas preservados; revisão humana pendente |
| G08 |0,5| README e reprodução | Modelo/digest, comandos, base, avaliação e notebooks publicados |

O PDF usa a expressão treinar LLM local no objetivo; o item G05 admite explicitamente LoRA ou agente. Foi seguida a alternativa de agente, sem apresentar isso como fine-tuning dos pesos. Relatório contém equipe/RMs, arquitetura, fontes/licenças, placares, erros e conclusão. Falta revisão final da equipe, vídeo publicado com URL real e envio.

## Vision — página 44

| Item | Peso / origem | Estado |
|---|---|---|
| Treino customizado | Objetivo oficial | YOLO26m ativo, 91 treino / 27 validação; cinco épocas concluídas de máximo 12; checkpoint escolhido na primeira |
| Comparação de fine-tuning | Evidência adicional | Checkpoints nano antigo/recente e controle, nove épocas cada; fase M registrada separadamente |
| GitHub | Entregável | Código, metadados, rótulos e comandos; mesmo checkpoint Vision em vision/release e três fotos com créditos em vision/examples; Qwen baixado e conferido por digest |
| PDF específico | Até 5 pontos | Atualizado: resumo 250 palavras, objetivo 50, equipe, método, ferramentas, resultados e conclusão |
| Vídeo funcionando | Até 5 pontos | Roteiro e API reais; gravação/publicação e URL pendentes |

Perfil efetivo: CPU, 960 pixels e confiança 0,25. Na mesma validação: precisão 70,3%, recall 67,2%, macrorecall 63,1%. Na regressão exposta de 23 fotos: precisão 68,3%, recall 62,1%, 41 TP / 19 FP / 25 FN. São ganhos agregados frente ao nano anterior, com regressões em algumas classes. Meta conjunta observada no lote básico13; não é prova de desempenho geral. A rubrica não fixa recall, número de fotos/classes/épocas ou duração do vídeo. quality_validated=false.

A decisão foi congelada antes da regressão; a emenda do objetivo balanceado veio após observar desenvolvimento e foi divulgada. Não chamar esse processo de teste cego independente. Fonte COCO e casos já examinados limitam generalização. Relatórios: vision/reports/finetune91-summary.json e ft91-medium-regression23.json.

## Ações restantes

1. Revisar nomes/RMs, conteúdo, gabaritos/respostas e relatórios com a equipe. Fichas de revisão humana não foram preenchidas pelo agente.
2. Gravar os dois vídeos, revisar imagem/voz/créditos, publicar no destino da equipe e inserir URLs reais. Regenerar PDF se alterar seu conteúdo.
3. Conferir acesso sem login e enviar em cada Teams até o prazo. Guardar comprovante.
4. Para uma próxima rodada, ampliar diversidade de cenas e reservar nova avaliação antes de ajustar o modelo. O lote de 50 fotos desta rodada já recebeu aprovação específica e foi usado: 26 treino / 11 validação / 13 teste, no experimento 117; candidato não promovido. Não há nova aprovação pendente desse lote. Critérios/limites em vision/reports/simple-next-proposal.json.

As aprovações dos lotes anteriores e a escrita GitHub estão resolvidas; não solicitar novamente o mesmo uso. Os ensaios locais atuais funcionam. O sistema não gravou/publicou vídeos nem enviou entregas ao Teams.


## Resultado final da expansão aprovada

O lote50 foi aprovado e compôs117treino/38validação/13teste, sem qualquer imagem dos23antigos. A adaptação117completou7épocas, mas o perfil equilibrado teveP71,5/R71,5 na validação, contraP72,7/R71,5 doM91; nenhum candidato passou a regra de promoção. O modelo ativo permanece treinado nas91fotos originais.

A decisão foi congelada antes do teste13. Uma avaliação única registrou52TP21FP20FN: precisão71,2%,recall72,2%,F10,7172; meta observada nesse pequeno conjunto básico. Macrorecall86,0%;12/13imagens tiveram ao menos um alvo primário correto, indicador suplementar que NÃO substituiP/Rglobais. Não é ganho causado pelo treino117 e não comprova generalização; fonteCOCO pode sobrepor pré-treino. As23complexas continuam com68,3%P/62,1%R, sem nova avaliação.

Não há aprovação de fotos pendente desta rodada. Restam revisão da equipe, vídeos, links reais e envio acadêmico. Perfil/erros/fontes completos em entregas/VISION_FINETUNING.md, vision/reports/finetune117-summary.json e ft117-reserved13.json. quality_validated=false permanece correto.
