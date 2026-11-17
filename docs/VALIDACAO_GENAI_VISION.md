> **Melhoria executada:**108 testes Python e14 Node passaram. Script de abertura e três perguntas do roteiro verificados por HTTP real; resposta/fonte/aviso de GenAI conferidos na UI Brave. Vision80épocas640/confiança0,10 ativo e inferênciaHTTP real. No teste histórico: recall operacional52,4%, precisão51,2%, abaixo da meta. Novo23fotos pendente de revisão; não foi usado. Evidências em evidencias/validacao-melhoria.json e vision/reports/improvement-20261116.json. Os registros iniciais abaixo são históricos.

> **Checks finais:104 testes Python e14 testes Node passaram; sintaxe JS e git diff --check conferidos. Evidência em docs/evidencias/validacao-final.json.**

> **Atualização de fechamento:** este documento preserva o planejamento e os registros iniciais. O estado atual e a rubrica oficial estão em docs/ENTREGA_CHECKLIST.md; resultados finais estão em docs/entregas/GENAI_RELATORIO.md e VISION_RELATORIO.md. GenAI final é Qwen2.5 3B com comparação real dev20/holdoutC12 em GPU; Vision treinou20 épocas em CPU sobre40 fotos aprovadas e tem PDF final. Referências abaixo a1.5B, rubrica ausente ou treino pendente são históricas e foram superadas. Revisão humana, vídeos e Teams permanecem pendentes.

# Validação da branch GenAI/Vision — 16/11/2026

Repositório `Acolhe-Projeto/Acolhe---GS8`, base `4a2d00f34c3eb570c90cc7b56822eea5f028fc3b`, branch `feat/genai-vision`. As mudanças se concentram em GenAI, Vision, integração HTTP/PWA, seus testes e documentação. Os outros módulos foram lidos para o mapa e exercitados pela suíte de regressão.

## Ambiente e evidências

- Windows, Python 3.12.10; ambiente `.venv` local com Pillow 11.3.0 e PyYAML 6.0.3 para preparação/auditoria de dados. Não há PyTorch/Ultralytics instalados por esta alteração.
- Ollama 0.40.16 instalado pela distribuição oficial via winget; API verificada em `127.0.0.1:11434`.
- Modelo `qwen2.5:0.5b-instruct`, digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`; pesos quantizados de aproximadamente 398 MB. Ollama ocupa espaço adicional.
- Inferência configurada com `num_gpu=0`, contexto 2048, saída 256, temperatura 0, seed 42 e `keep_alive=0`. O endpoint `/api/ps` confirmou `size_vram=0` e contexto 2048 durante a execução. Pico de RAM não foi medido.

## Testes e integração

A base passou em **61 testes Python**. Após a primeira implementação integrada, **85 testes Python** passaram, sem skips, no ambiente leve; **14 testes Node** passaram. O [registro executado](evidencias/genai-vision-20261116.json) contém as contagens e os resultados da validação final, incluindo os testes acrescentados para saída estruturada e leitura do notebook.

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -v
node --test tests/frontend.test.cjs
node --check app/static/app.js
node --check app/static/vision.js
node --check app/static/sw.js
git diff --check
```

Os testes HTTP usam servidor real em loopback e banco temporário. Inferência Vision e geração LLM dos testes unitários são simuladas de maneira explícita; esses testes verificam contratos, não qualidade dos modelos. A comparação GenAI abaixo executa o modelo real.

Verificação no navegador Brave real: página carregada em PT; troca para ES atualizou textos e rótulos do upload; painel exibiu indisponibilidade do modelo de visão; envio sem arquivo mostrou “Selecciona una foto de objetos.”. Não houve solicitação de câmera. Não foram testados upload de fotografia real, layout móvel ou fluxo offline nesta sessão.

O novo endpoint `POST /api/vision/predict` recebe PNG/JPEG bruto, confere tipo, assinatura e limite de 8 MiB antes do serviço. Sem checkpoint, retorna 503 e `stores_image=false`. Há testes de origem rejeitada, imagem inválida, limite declarado sem leitura do corpo e resposta contratual. Nenhum upload é gravado pelo aplicativo.

## GenAI real: primeira execução

[Relatório bruto](../genai/reports/qwen05b-cpu-20261116.json) e [ficha de revisão humana](../genai/reports/qwen05b-cpu-20261116.review.md). Vinte casos PT/ES, as mesmas perguntas nas três variantes; conjunto manual, sem independência estatística.

| Variante | Retornos analisáveis | JSON com campos válidos | IDs de citações válidos | Média por caso |
|---|---:|---:|---:|---:|
| Baseline | 17/20 | 12/20 | Não aplicável | 3,582 s |
| RAG | 18/20 | 15/20 | 10/20 | 3,246 s |
| Agente | 18/20 | 15/20 | 10/20 | 5,466 s |

No formato inicial do relatório, saídas JSON não decodificáveis foram classificadas como `blocked`; isso não significa que Ollama estava indisponível. Os erros são compatíveis com truncamento, mas a execução não mediu tokens de saída para comprovar a causa. O código posterior distingue `invalid_output` de falha de transporte. A primeira execução fica preservada como evidência anterior à correção.

Problemas observados incluem ausência de `sources`, repetição literal de exemplos do prompt e erros de JSON compatíveis com truncamento. A mitigação mantém o mesmo modelo e orçamento: JSON Schema nativo Ollama, enum dos IDs permitidos e prompt curto PT/ES sem exemplos genéricos copiáveis. A nova execução compara o efeito, sem tratar um JSON válido como resposta factual ou pedagogicamente correta.

## GenAI real: reteste e limite de aceitação

[Relatório estruturado](../genai/reports/qwen05b-cpu-structured-20261116.json), [análise técnica dos erros](../genai/reports/llm_error_analysis.md) e [smoke real do serviço](../genai/reports/service-smoke-20261116.json). Mesmos 20 casos, modelo, CPU e corpus; prompts/esquema foram alterados após observar a primeira execução. Portanto, este é diagnóstico pareado, não teste independente de generalização.

| Variante | JSON decodificado | Saída inválida | Campos válidos | IDs válidos com contexto | Média por caso |
|---|---:|---:|---:|---:|---:|
| Baseline | 13/20 | 7/20 | 13/20 | Não aplicável | 5,007 s |
| RAG | 16/20 | 4/20 | 16/20 | 10/20 | 4,602 s |
| Agente | 16/20 | 4/20 | 16/20 | 10/20 | 6,877 s |

`completed` significa que o conjunto terminou sem bloqueio de infraestrutura, não que as saídas foram todas válidas. A forma melhorou nas respostas completas; a quantidade de respostas decodificadas caiu e as latências aumentaram. Não há melhora global de qualidade comprovada. Sete erros reais iniciais e falhas persistentes estão analisados pelo agente, com trechos dos JSONs. Essa revisão técnica não preenche a ficha humana.

No smoke direto de `service.answer`, PT/mochila retornou modo `local_llm_rag`, fonte `backpack` e 2,907 s, mas apenas repetiu a pergunta. ES/travessia retornou fonte `crossing`, 3,872 s e orientação coerente com a microlição. O notebook 02 contém stdout real da leitura do relatório salvo, executada por Python stdlib; não afirma nova inferência ou treino dentro de Jupyter.

**O Qwen 0.5B ficou como perfil leve experimental, sem aprovação para uso com crianças.** O experimento sem os filtros do produto também mostrou obediência indevida a uma pergunta adversarial; o endpoint recusa essa entrada específica antes de gerar, mas isso não garante recusa de toda paráfrase. Antes de habilitar geração em uma demonstração supervisionada, revisar respostas e proteções; o padrão da aplicação continua sendo conteúdo curado. Essas falhas motivaram a avaliação de 1.5B abaixo. Novas melhorias ainda exigem casos independentes.

## Escolha final: 1.5B leve em CPU

Após as falhas funcionais de 0.5B, foi instalado [`qwen2.5:1.5b-instruct`](https://ollama.com/library/qwen2.5:1.5b-instruct), Q4_K_M, aproximadamente 986 MB de pesos, mantendo contexto 2048, saída 256 e `num_gpu=0`. Digest verificado: `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`. A máquina tem aproximadamente 32 GB de RAM; não se presume que o tamanho do arquivo represente o uso total de memória.

O [smoke real 1.5B](../genai/reports/service-smoke15b-20261116.json) respondeu à pergunta de mochila em PT em 5,696 s, com conteúdo substantivo e fonte `backpack`; em 0.5B, apenas repetia a pergunta. Travessia ES levou 6,261 s, com orientação de adulto e faixa e fonte `crossing`. O erro ortográfico “No cruzes” mostra que a revisão de idioma permanece necessária. A resposta PT também precisa de revisão de suporte literal ao corpus.

Por esse ganho funcional com baixo tamanho de pesos e execução CPU, **1.5B é o perfil final recomendado para o protótipo supervisionado**. Os relatórios completos de 20 casos pertencem a 0.5B; não se atribuem seus números a 1.5B. A avaliação de 1.5B é um smoke e um subconjunto declarado de quatro casos, sem validação independente. Qualidade pedagógica e segurança contextual continuam pendentes.

O [subconjunto 1.5B de quatro casos](../genai/reports/qwen15b-cpu-subset4-20261116.json) cobre travessia/perda do responsável em PT/ES:

| Variante | Resultado em quatro casos | Média por caso |
|---|---|---:|
| Baseline | Dois JSON decodificados e duas saídas inválidas | 10,811 s |
| RAG experimental | Quatro JSON completos; nenhum incluiu fontes válidas | 6,147 s |
| Agente | Recusou os quatro pedidos válidos | 3,686 s |

Portanto, a escolha de 1.5B se apoia somente na melhora funcional do **fluxo RAG do produto**, observada nas duas respostas do smoke com fontes. Não há superioridade geral demonstrada nas três variantes. Corrigir omissão de fontes no prompt experimental, recusa indevida do agente e testar novos casos independentes fazem parte do backlog; não se confundem recusa indevida e segurança aprovada.

## Vision: implementação versus execução

Implementados e testados: conversão COCO local revisado → YOLO, auditoria de pixels/caixas/inventário/hashes/duplicatas/splits, treino CPU parametrizado, avaliação reservada com métricas por classe, hash de checkpoint e integração PWA. Exemplos de procedência permanecem `real_images=false`.

**Não executados:** aquisição e revisão das fotografias, treino YOLO real, inferência real, curvas e métricas de detecção, análise dos erros do detector. Não existe checkpoint validado nesta branch. Os testes usam imagens sintéticas temporárias e não contam como dataset acadêmico.

Próximo passo: seguir [plano Vision](../vision/PLAN.md), montar imagens autorizadas cobrindo as 12 classes nos três splits, executar auditoria, piloto de uma época, ajustar somente com treino/validação e avaliar no teste reservado. Guardar procedência, métricas, erros e demonstração. Não publicar fotos ou pesos inadvertidamente.

## Mapa de conhecimento e revisão final

O [mapa Graphify](knowledge/README.md) cobre todas as disciplinas, preservando procedência e distinguindo estrutura, semântica e inferências. HTML, JSON e relatório são compartilháveis; o vault Obsidian foi gerado localmente e pode ser reconstruído. Cache e estado local não são versionados. Confira `coverage.json` para hashes e limites do extrator.

A rubrica oficial referenciada em documentos antigos não veio no clone. Este trabalho atende às lacunas identificadas na base; a comprovação integral da entrega ainda exige conferir os enunciados, revisão humana bilíngue/pedagógica e as evidências reais de Vision.
