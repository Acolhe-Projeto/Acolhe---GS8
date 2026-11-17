# Checklist atual — GenAI e Vision

Atualizado17/11/2026. Branch feat/genai-vision. Esta versão substitui a auditoria inicial, preservada no histórico Git. Evidência distingue implementação, execução e qualidade; não concede nota.

## Fonte oficial e prazo

Desafio-FIAP-GS-CitizenTech4ES,60páginas, SHA256236c35530bc23f3f6c48211f022862ff5d1458f17ad2d813e1f9d5130b696c87. Fonte local em Downloads. Páginas24,29–31 e 44 conferidas. Prazo19/11 às23h55, no Teams de cada disciplina; um integrante envia, links públicos funcionando durante correção. Conferir horário no ambienteFIAP.

## GenAI — pesos da página30

| ID | Peso | Critério | Estado atual / o que falta |
|---|---:|---|---|
| G01 |0,5| Tarefa e gabarito, incluindo não consta | Implementado: mobilidade educativa, dev20/holdoutC12 e negativas; revisar conteúdo com humanos |
| G02 |1,0| Base em trechos com fonte | Oito documentos bilíngues, atribuição/licença, base/ e CSV; revisão pedagógica pendente |
| G03 |1,0| Recall@1/@3 e limiar justificado | Medidos16/16 no desenvolvimento, limiar2.0; não confundir com acerto da resposta |
| G04 |2,0| JSON, citação e recusa fundamentada | API/UI reais e contratos válidos; falhas semânticas preservadas, sem afirmar perfeição |
| G05 |2,0| LoRA ou agente versus RAG | Agente real retrieve/refuse comparado; LoRA não é pendência obrigatória |
| G06 |2,0| Placar de três configurações interpretado | MesmoQwen3B, dev20/C12; julgamento técnico do agente separado de revisão humana |
| G07 |1,0| Cinco erros e correção proposta | Relatório rastreia erros reais; não foram inventados cinco casos para completar tabela |
| G08 |0,5| README/reprodutibilidade | Publicados comandos/base/avaliacao/notebooks/API e perfil; conferir execução/links finais |

Total10pontos conforme rubrica, sem previsão de nota. Relatório de página31 já contém equipe/RMs, ficha, Mermaid, base/licenças, placar, erros e conclusão. **Falta gravar/publicar vídeo e incluir URL real**, além de revisão final da equipe e envio no Teams. Revisão humana é necessária para qualificar os julgamentos atuais; não foi inventada uma pontuação adicional para isso.

Modelo finalQwen2.5:3b-instruct, abaixo de 4B, com GPU verificada. Revisão técnica de conteúdo emC12:baseline4/12, RAG8/12, agente9/12; não é acurácia humana cega. Guia rápido/roteiro90segundos: entregas/COMO_USAR_E_GRAVAR.md.

## Vision — página44

| Item | Peso / origem | Estado atual / o que falta |
|---|---|---|
| Treinamento customizado | Objetivo oficial | ExecutadoYOLO11n e YOLO26n; ativoYOLO26n 80 épocas640CPU, confiança 0,15 pela validação |
| GitHub código/documentação | Entregável | Branch publicada; fotos/pesos locais, instruções e metadados/rótulos para reconstrução |
| PDF específico | Até5pontos | Título, equipe, resumo250palavras, introdução, objetivo50palavras, ferramentas, método, resultados e conclusão; renderização conferida |
| Vídeo funcionando | Até5pontos | Pendente gravação, revisão, publicação e URL real; roteiro pronto |

Não há recall mínimo, número de fotos/classes/épocas ou duração de vídeo fixados na página44. **Meta local aprovada:70% de recall e 70% de precisão**, ainda não atingida. Na regressão23 já examinada:YOLO26n teve recall51,5%, precisão60,7%, F1 de 0,5574. Foi promovido por validação antes dessa medição. Não chamar regressão em teste exposto de nova avaliação independente. quality_validated=false.

Dados:40 fotos iniciais aprovadas; mais23 aprovadas exclusivamente para teste local. Treino25/val8 inalterados; teste 23 com 66 objetos. Não usar23 para treino ou publicar as fotos sem revisão da exibição. Modelos e resultados anteriores preservados.

## Ações restantes

1. Revisar nomes/RMs, conteúdoGenAI, gabaritos/respostas e relatórios; fichas humanas não foram preenchidas pelo agente.
2. Gravar os dois vídeos reais, revisar imagem/voz/créditos e publicar em destino da equipe. Inserir URLs nos relatórios e regenerar PDF se necessário.
3. Conferir acesso sem login aos links e enviar em cada Teams até o prazo. Guardar comprovante.
4. Para perseguir70%/70%, ampliar treino equilibrado e reservar outro teste final; não reusar teste 23 para escolher nova configuração. Isso é melhoria de qualidade, não novo critério numérico imposto pelo PDF.

SSO e escritaGitHub resolvidos. Aprovações dos lotes40 e 23 já registradas; não solicitar novamente o mesmo uso. O sistema não gravou/publicou vídeos nem enviou entregas ao Teams.
