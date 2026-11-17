> **Rodada de melhoria concluída:** Vision80épocas640/confiança0,10 ativo por seleção em validação; recall operacional52,4%, precisão51,2% no teste histórico. Meta70%/70% ainda não atingida. O lote novo23fotos foi aprovado e avaliado: recall53,0%, precisão48,6%; não entrou no treino. PDF regenerado; roteiro rápido em entregas/COMO_USAR_E_GRAVAR.md. Números20épocas/29,4% abaixo identificam o piloto inicial.

# Fechamento atual — GenAI e Vision

## O que ainda depende da equipe

1. Revisar respostas, conteúdo pedagógico, nomes/RMs e relatórios. Fichas humanas continuam pendentes; não inventamos aprovação.
2. Gravar/revisar/publicar os dois vídeos e inserir URLs reais. Antes de exibir fotos em vídeo público, revisar e autorizar essa publicação específica: o lote foi aprovado para treino local.
3. Conferir acessibilidade dos links e enviar em cada Teams até19/11/2026 às23h55 (horário do ambiente FIAP). Um integrante por disciplina.

SSO Git concluído; dry-run de escrita autorizado. Lote Vision v2 e anotação foram aprovados pelo usuário antes do treino. Essas duas aprovações não precisam ser solicitadas novamente.

| Critério | Estado atual / evidência |
|---|---|
| G01 tarefa/gabarito | Mobilidade educativa PT/ES; dev20 e holdoutC12 com respostas/fontes/recusas esperadas em genai/avaliacao/ |
| G02 base atribuída | Oito documentos bilíngues v2; fonte canônica, base/ e fontes.csv |
| G03 busca/limiar | recall@1 e@3:16/16 no desenvolvimento; limiar2.0 justificado em limiar.json; não generalizar para população |
| G04 JSON/fonte/recusa | Execução real3B e API; contratos válidos, falhas de conteúdo preservadas; revisão humana pendente |
| G05 LoRA ou agente | Agente real retrieve/refuse comparado ao mesmo modelo em RAG; LoRA não é obrigatório |
| G06 placar3configurações | qwen3b-v4-gpu-dev20.json e holdout12.json; revisão técnica exploratória separada, sem inflar acerto por ID válido |
| G07 cinco erros | Casos/saídas e hipóteses no relatório GenAI; correções propostas e limites explícitos |
| G08 reprodução | README, comandos, base/, avaliacao/, três notebooks com outputs reais; novo hardware pode variar |
| GR01–GR06 | Relatório específico GenAI com equipe, ficha, Mermaid, fontes/licença, placar e erros |
| GR07 | Conclusão e repositório prontos; URL de vídeo pendente |
| GA01–GA04 | Notebooks, base, avaliação e API integrada; evidência HTTP real no notebook03 |
| GA05/V02 | Branch de entrega: feat/genai-vision; fotos/pesos não são publicados nesta etapa |
| V01 treino customizado | YOLO11n20 épocasCPU,40 fotos aprovadas,25/8/7; hash/checkpoint/ambiente/métricas reais em vision/reports/ |
| V03/VP01–VP09 PDF | output/pdf/ACOLHE_VISION.pdf,5 páginas verificadas visualmente; resumo250 e objetivo50 palavras; resultados reais e limitações |
| V04 vídeo | Pendente gravação/revisão/publicação; roteiro em docs/entregas/ROTEIRO_VIDEOS.md |

Qualidade: Vision recall0,2943 e mAP500,3878 em apenas7 fotos de teste; quality_validated=false. GenAI holdoutC12 teve4/12,8/12,9/12 acertos na revisão técnica do agente (baseline/RAG/agente), ainda sem avaliação humana cega. Nenhum resultado garante nota ou prontidão para crianças. A rubrica oficial e pesos completos permanecem na auditoria histórica abaixo; estados antigos foram superados por esta matriz.

---

## Auditoria inicial preservada — estados históricos

# Checklist das entregas - GenAI e Computer Vision

Auditoria em 16/11/2026, branch `feat/genai-vision`. A base examinada foi o commit `a988d73f6a7e51731efb8c1d5a2da8cae2359af1`; há correções e experimentos em andamento nesta sessão. Os estados abaixo descrevem a evidência encontrada na auditoria, não uma nota prevista nem uma aprovação do professor. Atualizar a coluna de evidências quando os novos experimentos, documentos e vídeos estiverem concluídos.

## Fonte oficial e prazo

Fonte: PDF local `C:\Users\hyeon\Downloads\Desafio-FIAP-GS-CitizenTech 4ES.pdf`, 60 páginas, SHA-256 `236c35530bc23f3f6c48211f022862ff5d1458f17ad2d813e1f9d5130b696c87`. Foram lidas as páginas relevantes completas e conferidas visualmente as páginas 30, 31 e 44. A numeração aqui corresponde à posição da página no PDF, começando em 1.

Regras gerais da página 24:

- Entregar até **19/11/2026, às 23h55**, no Teams de **cada disciplina**. O documento não explicita fuso horário; conferir o horário mostrado no ambiente FIAP.
- Somente um integrante envia cada entrega. A equipe tem até cinco alunos da mesma turma e mantém o mesmo produto nas disciplinas.
- Repositórios, aplicações e vídeos devem permanecer acessíveis durante a correção, que pode ocorrer até uma semana após o encerramento.
- Cada disciplina vale 10 pontos. Os pesos específicos abaixo vêm das páginas 30 e 44.

O escopo desta matriz é **GenAI e Vision**, as duas matérias assumidas pelo responsável desta branch. Pendências de Big Data, BI, RPA, DevSecOps e Maker não foram convertidas em obrigações destas duas matérias. O produto compartilhado e os integrantes precisam continuar consistentes entre as entregas.

## O que precisa de uma ação ou aprovação externa

| Item | Ação concreta necessária | Responsável | O que já pode avançar localmente |
|---|---|---|---|
| Escrita no GitHub | Usar uma conta com permissão de escrita ou obter essa permissão no repositório da equipe. A tentativa de push desta branch retornou 403 | Integrante ou administrador do repositório | Código, commits locais, relatórios e preparação da branch |
| Imagens de Vision | Revisar o lote preparado, procedência, direitos de uso e ausência de pessoas identificáveis; registrar aprovação real antes do treino | Responsável humano pela curadoria | Seleção, inventário, folhas de revisão e validações técnicas; não marcar revisão humana como aprovada pelo agente |
| Respostas de GenAI | Revisar conteúdo, idioma PT/ES, suporte pelas fontes e recusas nas respostas efetivamente geradas | Integrante e, quando necessário, revisor pedagógico | Correções, avaliações automáticas e análise técnica identificada como feita pelo agente |
| Vídeos | Gravar as demonstrações reais, revisar o material e autorizar publicação no destino da equipe | Equipe | Roteiro, comandos, cenários e pacote de evidências |
| Envio no Teams | Conferir os links finais e enviar na disciplina correta antes do prazo | Um integrante por disciplina | Checklist e texto de entrega preparados para revisão |
| Adequação do problema GenAI | Manter a tarefa principal em energia, segurança ou mobilidade. Se a equipe pretender apresentar predominantemente vocabulário geral, esclarecer o enquadramento com o professor | Equipe/professor | Delimitar e demonstrar mobilidade segura no relatório e nos testes |

A página 29 estabelece o domínio da atividade, mas **não exige aprovação prévia formal do professor**. A consulta sobre o enquadramento é uma recomendação para evitar uma entrega fora do domínio, não uma regra de autorização inventada. A revisão de imagens e respostas é uma dependência do procedimento do projeto; não aparece como item separado com pontuação no slide.

Correções reversíveis, testes locais, preparação dos relatórios e experimentos já autorizados não exigem uma nova aprovação por etapa. Publicação e submissão devem usar somente o pacote concreto revisado pela equipe.

## GenAI - critérios com pontuação

Professor: Francisco Elanio Bezerra. Enunciado e objetivo na página 29; pesos na página 30. A atividade trata de uma LLM local aplicada a energia, segurança ou mobilidade e pede evidência de mais acertos e menos alucinações em relação ao **mesmo modelo sem contexto**, integrada ao produto.

| ID | Peso | Critério oficial, em outras palavras | Código/evidência encontrada | Falta para comprovar integralmente | Responsável / dependência |
|---|---:|---|---|---|---|
| G01 | 0,5 | Definir a tarefa e testar com gabarito, incluindo casos em que a resposta não existe na base | `genai/PLAN.md`; 16 questões com documento esperado em `genai/evaluate.py`; quatro questões negativas em `genai/experiment.py` | Registrar gabarito de resposta/recusa e regra de julgamento para cada caso; documento relevante sozinho não é gabarito de correção semântica. Delimitar mobilidade/segurança | Implementação e documentação; revisão humana do gabarito |
| G02 | 1,0 | Disponibilizar conhecimento dividido em trechos atribuídos a fontes | `genai/data/corpus.json`: oito microlições PT/ES com IDs, fonte e licença declarada | Consolidar tabela fonte/formato/licença/quantidade de trechos; revisar adequação ao domínio e conteúdo. Não tratar a declaração autoral como validação pedagógica | Implementação/documentação e revisão de conteúdo |
| G03 | 1,0 | Medir recall@1 e recall@3 e justificar um limiar de busca | `genai/evaluate.py`, `genai/reports/retrieval.json`, notebook 01; histórico de 0,6875 nas duas métricas sobre 16 casos | Documentar e justificar o limiar de aceitação/recusa com o conjunto de validação; repetir medições após mudanças e identificar conjunto/denominador. `score > 0` sem justificativa não fecha o item | Implementação e experimento real |
| G04 | 2,0 | Gerar resposta fundamentada em JSON, com fonte e recusa apropriada | `genai/service.py`, API `/api/assistant`, testes e smokes reais PT/ES | Corrigir fontes omitidas, JSON incompleto e falsas recusas; verificar suporte textual da resposta, não somente pertencimento do ID à base; testar integração real com o perfil final | Implementação/experimentos; revisão humana de conteúdo |
| G05 | 2,0 | Comparar uma especialização por LoRA **ou agente** com o RAG simples | `genai/compare.py` implementa decisão `retrieve/refuse` e rastro. No subconjunto histórico 1.5B, o agente recusou quatro pedidos pertinentes | Corrigir e executar a especialização no conjunto final; demonstrar o comportamento e interpretar o resultado frente ao RAG. A existência do arquivo ou um mock não comprova agente útil | Implementação e inferência real |
| G06 | 2,0 | Produzir um placar interpretado das três configurações | Relatórios históricos de 20 casos em 0.5B e de quatro casos em 1.5B, com latências, JSON e IDs | Completar baseline/RAG/agente com o **mesmo modelo final e mesmas questões**. Acrescentar julgamento de acerto e alucinação com definição explícita; não usar JSON/IDs como sinônimo de qualidade. Nova rodada final em andamento nesta sessão | Experimento final e revisão dos resultados |
| G07 | 1,0 | Apresentar cinco erros realmente observados e propor correções | `genai/reports/llm_error_analysis.md` documenta erros reais e intervenções com referência aos JSONs | Selecionar cinco casos rastreáveis da execução relevante, com trecho, causa provável, proposta e resultado do reteste quando feito. Preservar falhas antigas como históricas; não atribuí-las silenciosamente ao modelo final | Análise técnica; validação humana quando avaliar conteúdo |
| G08 | 0,5 | Explicar no README como reproduzir a entrega | `genai/README.md`, `genai/local.py`, testes e parâmetros de runtime | Validar instruções do pacote final, versões/modelo/digest, caminho dos dados, comandos e saída esperada; publicar a revisão correta e conferir acesso público | Implementação/documentação; acesso GitHub |

**Total oficial: 10,0 pontos.** Nenhuma soma de pontos foi concedida nesta auditoria: o professor avalia a suficiência e a qualidade das evidências.

### GenAI - conteúdo obrigatório do relatório e do repositório

A página 31 acrescenta os itens abaixo. A página 29 também exige a API, base de conhecimento, testes, notebooks com saídas e README em repositório público.

| ID | Item da entrega | Estado encontrado / evidência | O que fechar |
|---|---|---|---|
| GR01 | Nomes completos e RMs | Os quatro integrantes constam do README principal | Conferir com a equipe e incluir também no relatório específico GenAI |
| GR02 | Ficha técnica e descrição da tarefa | Há informações em README/PLAN/PRD | Consolidar problema, usuário, domínio, modelo, runtime, parâmetros, dados e limitações no relatório |
| GR03 | Diagrama do pipeline e dos documentos | Mermaid no PRD e nos planos dos módulos | Incluir a cadeia documentos/trechos/busca/geração/especialização/API e vincular aos arquivos reais |
| GR04 | Tabela da base com fonte, formato, licença e número de trechos | JSON registra fonte/licença por microlição; tabela consolidada ainda não estava na base auditada | Produzir a tabela com contagens verificadas e deixar revisão do conteúdo explícita |
| GR05 | Performance das configurações testadas | Há relatórios reais históricos e smokes | Fechar o placar do mesmo modelo final com todas as configurações, denominadores e interpretação. Não prometer superioridade se os resultados não a sustentarem |
| GR06 | Cinco erros com causa e correção proposta | Análise técnica existente | Referenciar casos exatos do relatório, sem inventar respostas ou avaliações humanas |
| GR07 | Conclusão técnica e links do repositório e vídeo | Conclusões parciais existem; vídeo específico não foi encontrado | Concluir após executar, gravar demonstração real e incluir os links públicos verificados |
| GA01 | Pasta `notebooks/` com saídas salvas | `genai/notebooks/01_retrieval.ipynb` e `02_local_llm.ipynb`; o segundo lê um relatório real salvo | Manter código para reprodução e saídas representativas do pipeline final. Distinguir leitura de relatório, inferência e treinamento; não alegar execução Jupyter inexistente |
| GA02 | Pasta `base/` com trechos e fontes | Conhecimento está em `genai/data/` | Expor a estrutura solicitada pela página 31, ou um índice inequívoco em `base/` apontando à fonte canônica, sem duplicação divergente |
| GA03 | Pasta `avaliacao/` com testes e placar | Arquivos atualmente distribuídos entre `evaluate.py`, `experiment.py`, testes e `reports/` | Organizar o pacote de avaliação na estrutura solicitada, com gabarito, resultados e comandos claros |
| GA04 | API e integração | `/api/assistant` existe; testes HTTP cobrem contratos, smokes diretos cobrem geração | Demonstrar pergunta, recuperação, resposta/fontes e recusa no produto com o modelo habilitado; registrar versão, comando e evidência |
| GA05 | Repositório público com a revisão final | O repositório existe; a branch de trabalho ainda não pôde ser enviada por falta de permissão | Publicar a branch/revisão correta e testar os links sem sessão autenticada |

O nome da atividade fala em treinamento local, mas o critério G05 aceita expressamente **LoRA ou agente**. Não é correto transformar fine-tuning/LoRA em exigência obrigatória quando a equipe escolhe e comprova o agente. Também não é correto chamar simples recuperação de conteúdo de treinamento ou geração por LLM.

### GenAI - aprovações e evidências que não devem ser simuladas

- Uma revisão técnica feita pelo agente deve ser identificada como tal. As fichas humanas não podem receber notas inventadas.
- As métricas precisam medir o que seus nomes afirmam. Validade de JSON e de IDs não prova acerto, redução de alucinação nem segurança contextual.
- Melhora observada em duas perguntas do serviço não substitui o placar comparativo nem demonstra superioridade geral.
- O PDF não fixa tamanho de modelo, GPU, número mínimo de perguntas ou meta numérica de recall. Usar CPU/GPU, 20 perguntas ou metas locais é decisão de engenharia e deve ser documentada como tal.

## Applied Computer Vision - critérios e entregáveis

Professores: Arnaldo Viana e Paulo Rodrigues. Páginas 43 e 44. O objetivo explícito é **treinamento customizado** de uma arquitetura adequada ao problema para detecção de objetos ou realidade aumentada. Código preparado, pesos genéricos prontos e respostas simuladas não substituem essa execução.

| ID | Peso / origem | Critério ou item | Evidência encontrada | O que falta para fechar | Responsável / dependência |
|---|---|---|---|---|---|
| V01 | Objetivo, p.44 | Treinar uma arquitetura customizada para o problema | `vision/train.py` prepara transferência de YOLO11n; dataset, checkpoint e métricas reais não estavam na base auditada | Aprovar as imagens revisadas, executar treino real, salvar configuração, ambiente, pesos/hash e registro de execução. Preparação de lote público em andamento; treino aguarda aprovação humana | Curadoria humana + execução local |
| V02 | Entregável, p.44 | Repositório GitHub com código e documentação completos | Serviços, preparação, auditoria, testes e README existem | Publicar a revisão final com instruções, procedência compartilhável, relatório e links; confirmar acesso público. Não publicar imagens/pesos sem direito de redistribuição | Implementação/documentação + acesso GitHub |
| V03 | Até 5,0, p.44 | PDF específico com todos os conteúdos pedidos | Há manual geral, PRD e planos. Nenhum PDF específico de Vision com todos os itens foi encontrado na base auditada | Produzir e revisar o PDF abaixo com resultados reais. Um manual geral não comprova esse conjunto de itens | Relatório após experimento; revisão da equipe |
| V04 | Até 5,0, p.44 | Vídeo que demonstra a solução funcionando | Não foi encontrado vídeo específico de Vision publicado e verificável | Gravar o detector customizado realmente funcionando, explicar dados/treino/resultados/limites e inserir link no relatório/repositório | Gravação, aprovação e publicação pela equipe |

### Conteúdo do PDF Vision - peso conjunto de até 5 pontos

O slide não distribui os cinco pontos entre as seções. Não foi inventado peso individual.

| ID | Seção requerida, p.44 | Estado da base auditada | Ação necessária |
|---|---|---|---|
| VP01 | Título | Nome do produto existe | Identificar problema de detecção e o módulo na capa/título |
| VP02 | Integrantes | Nomes/RMs no README geral | Incluir identificação da equipe no PDF e conferir grafia/RMs |
| VP03 | Resumo de **250 palavras** | Não encontrado como seção contada de relatório Vision | Redigir após os resultados; conferir contagem por regra explícita |
| VP04 | Introdução | Contexto no manual/PRD | Explicar problema, público e por que detecção de objetos contribui para o Acolhe |
| VP05 | Objetivo de **50 palavras** | Objetivo narrativo nos planos, sem seção final contada | Redigir objetivo específico de Vision e conferir contagem |
| VP06 | Explicação técnica das ferramentas | README descreve YOLO e dependências | Explicar arquitetura escolhida, transferência, runtime, bibliotecas e limites com as versões realmente usadas |
| VP07 | Metodologia passo a passo | Preparação/auditoria/treino descritos e implementados | Relatar dados, curadoria, classes, separação, parâmetros, treino e avaliação executados, com rastreabilidade |
| VP08 | Exemplos de resultados | Apenas contratos simulados; treino/inferência reais ausentes na base auditada | Inserir saídas reais, imagens autorizadas e erros/limites; não usar fixtures de testes como evidência de modelo |
| VP09 | Conclusão | Planos identificam pendências | Concluir a partir dos resultados reais e separar piloto técnico de qualidade validada |

### O que é recomendação de engenharia, e não exigência numérica da página 44

A página não estipula quantidade de classes/imagens, proporção de splits, número de épocas, arquitetura YOLO, mAP mínimo, duração do vídeo nem formato exato de inventário. As 12 classes, seed 42, resolução 320, batch pequeno, treino/val/teste, métricas por classe, hashes e análise de erros são decisões do projeto para tornar a execução rastreável e convincente. Não devem ser apresentadas como números obrigatórios da rubrica.

Mesmo sem uma pontuação separada para cada prática, resultados sem dados e método verificáveis dificultam comprovar o treinamento customizado e os exemplos de resultados pedidos. Por isso, o inventário, a revisão de privacidade, as métricas reais e o checkpoint são dependências técnicas da entrega escolhida.

## Fechamento operacional

| Ordem | Ação | Dependência antes de marcar concluído |
|---:|---|---|
| 1 | Corrigir GenAI e executar conjunto final comparável | Inferência real do mesmo modelo nas três configurações, gabarito e definições das métricas |
| 2 | Preparar pacote de imagens para revisão | Procedência/licenças registradas e imagens apresentadas para decisão humana |
| 3 | Executar Vision customizado | Aprovação real do lote, ambiente funcional e registro do treino/avaliação |
| 4 | Consolidar relatórios e notebooks | Resultados efetivos; PDF Vision com 250/50 palavras conferidas |
| 5 | Revisar respostas e resultados | Avaliação humana identificada, sem confundir testes automatizados com aprovação pedagógica |
| 6 | Gravar e publicar vídeos | Solução demonstrável e revisão/autorização do material concreto |
| 7 | Publicar a revisão correta no GitHub | Conta com permissão de escrita; links públicos conferidos |
| 8 | Enviar em cada Teams | Um integrante responsável, links corretos, prazo confirmado |

O fechamento exige conferir os artefatos novos da sessão contra esta matriz. Não há base para afirmar que todos os dez pontos de qualquer disciplina foram obtidos apenas porque os testes de software passaram.
