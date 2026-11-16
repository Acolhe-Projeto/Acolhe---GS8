# Graph Report - Acolhe---GS8  (2026-11-16)

## Corpus Check
- Corpus: 104 supported source files, approximately 49,208 words; generated knowledge outputs excluded.

## Summary
- 864 nodes · 1406 edges · 65 communities (34 shown, 31 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 43 edges (avg confidence: 0.86)
- Token cost: not metered input · not metered output

## Graph Freshness
- Built from commit: `4a2d00f3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Objetos e treinamento Vision 0|Objetos e treinamento Vision 0]]
- [[_COMMUNITY_Tutor e avaliação GenAI 1|Tutor e avaliação GenAI 1]]
- [[_COMMUNITY_Engenharia de dados 2|Engenharia de dados 2]]
- [[_COMMUNITY_Engenharia de dados 3|Engenharia de dados 3]]
- [[_COMMUNITY_Contratos e regressões 4|Contratos e regressões 4]]
- [[_COMMUNITY_Robô e segurança 5|Robô e segurança 5]]
- [[_COMMUNITY_Configuração do projeto 6|Configuração do projeto 6]]
- [[_COMMUNITY_Documentação e evidências 7|Documentação e evidências 7]]
- [[_COMMUNITY_Objetos e treinamento Vision 8|Objetos e treinamento Vision 8]]
- [[_COMMUNITY_Pipeline de integração 9|Pipeline de integração 9]]
- [[_COMMUNITY_Aplicação e interface 10|Aplicação e interface 10]]
- [[_COMMUNITY_Documentação e evidências 11|Documentação e evidências 11]]
- [[_COMMUNITY_Objetos e treinamento Vision 12|Objetos e treinamento Vision 12]]
- [[_COMMUNITY_Contratos e regressões 13|Contratos e regressões 13]]
- [[_COMMUNITY_Pipeline de integração 14|Pipeline de integração 14]]
- [[_COMMUNITY_Configuração do projeto 15|Configuração do projeto 15]]
- [[_COMMUNITY_Objetos e treinamento Vision 16|Objetos e treinamento Vision 16]]
- [[_COMMUNITY_Tutor e avaliação GenAI 17|Tutor e avaliação GenAI 17]]
- [[_COMMUNITY_Tutor e avaliação GenAI 18|Tutor e avaliação GenAI 18]]
- [[_COMMUNITY_Documentação e evidências 19|Documentação e evidências 19]]
- [[_COMMUNITY_Infraestrutura e observabilidade 20|Infraestrutura e observabilidade 20]]
- [[_COMMUNITY_Infraestrutura e observabilidade 21|Infraestrutura e observabilidade 21]]
- [[_COMMUNITY_Infraestrutura e observabilidade 22|Infraestrutura e observabilidade 22]]
- [[_COMMUNITY_Documentação e evidências 23|Documentação e evidências 23]]
- [[_COMMUNITY_Pipeline de integração 24|Pipeline de integração 24]]
- [[_COMMUNITY_Tutor e avaliação GenAI 25|Tutor e avaliação GenAI 25]]
- [[_COMMUNITY_Configuração do projeto 26|Configuração do projeto 26]]
- [[_COMMUNITY_Infraestrutura e observabilidade 27|Infraestrutura e observabilidade 27]]
- [[_COMMUNITY_Infraestrutura e observabilidade 28|Infraestrutura e observabilidade 28]]
- [[_COMMUNITY_Documentação e evidências 29|Documentação e evidências 29]]
- [[_COMMUNITY_Indicadores e negócio 30|Indicadores e negócio 30]]
- [[_COMMUNITY_Aplicação e interface 31|Aplicação e interface 31]]
- [[_COMMUNITY_Engenharia de dados 32|Engenharia de dados 32]]
- [[_COMMUNITY_Pipeline de integração 33|Pipeline de integração 33]]
- [[_COMMUNITY_Configuração do projeto 34|Configuração do projeto 34]]
- [[_COMMUNITY_Tutor e avaliação GenAI 35|Tutor e avaliação GenAI 35]]
- [[_COMMUNITY_Aplicação e interface 36|Aplicação e interface 36]]
- [[_COMMUNITY_Engenharia de dados 37|Engenharia de dados 37]]
- [[_COMMUNITY_Infraestrutura e observabilidade 38|Infraestrutura e observabilidade 38]]
- [[_COMMUNITY_Aplicação e interface 39|Aplicação e interface 39]]
- [[_COMMUNITY_Infraestrutura e observabilidade 40|Infraestrutura e observabilidade 40]]
- [[_COMMUNITY_Tutor e avaliação GenAI 41|Tutor e avaliação GenAI 41]]
- [[_COMMUNITY_Tutor e avaliação GenAI 42|Tutor e avaliação GenAI 42]]
- [[_COMMUNITY_Tutor e avaliação GenAI 43|Tutor e avaliação GenAI 43]]
- [[_COMMUNITY_Configuração do projeto 44|Configuração do projeto 44]]

## God Nodes (most connected - your core abstractions)
1. `HttpTests` - 19 edges
2. `audit()` - 19 edges
3. `answer()` - 17 edges
4. `CoreTests` - 17 edges
5. `run()` - 14 edges
6. `compare()` - 14 edges
7. `ExperimentTests` - 14 edges
8. `DatasetTests` - 14 edges
9. `Store` - 13 edges
10. `Handler` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Baseline RAG agente` --semantically_similar_to--> `Treino customizado e split`  [INFERRED] [semantically similar]
  genai/README.md → vision/README.md
- `Handler` --uses--> `ModelUnavailable`  [INFERRED]
  app/server.py → vision/service.py
- `CoreTests` --uses--> `Store`  [INFERRED]
  tests/test_core.py → app/core.py
- `HttpTests` --uses--> `ModelUnavailable`  [INFERRED]
  tests/test_http.py → vision/service.py
- `create_server()` --calls--> `Store`  [EXTRACTED]
  app/server.py → app/core.py

## Import Cycles
- None detected.

## Communities (65 total, 31 thin omitted)

### Community 0 - "Objetos e treinamento Vision 0"
Cohesion: 0.07
Nodes (19): DeploymentContractTests, Vision dados treino e integração, audit(), confined(), reviewed_record(), Notebook treino não executado, Planejamento Vision CPU, prepare() (+11 more)

### Community 1 - "Tutor e avaliação GenAI 1"
Cohesion: 0.06
Nodes (24): Rubrica GenAI relatada, GenAI Qwen local leve, compare(), evaluate(), recall_at(), llm_notebook(), cases(), run() (+16 more)

### Community 2 - "Engenharia de dados 2"
Cohesion: 0.06
Nodes (18): official_snapshots(), acquire(), collect(), normalize_municipalities(), save_snapshot(), Dois dias reais de coleta, Fontes, autoria e licencas, Fontes oficiais: coleta real separada da demonstracao (+10 more)

### Community 3 - "Engenharia de dados 3"
Cohesion: 0.07
Nodes (21): acolhe(), medallion(), create_demo(), run(), validated(), Adaptador de fontes reais, Airflow, Airflow e Databricks pendentes (+13 more)

### Community 4 - "Contratos e regressões 4"
Cohesion: 0.07
Nodes (12): create_server(), Evidência da branch, assert, fs, harness(), lesson, source, test (+4 more)

### Community 5 - "Robô e segurança 5"
Cohesion: 0.07
Nodes (17): Arquitetura modular local, RPA e Maker demonstrações, Robô somente simulado, Gateway, react(), sensor_context(), main(), RobotTests (+9 more)

### Community 6 - "Configuração do projeto 6"
Cohesion: 0.06
Nodes (26): public_lessons(), Acolhe: plano de implementação, MVP integrado, Inicializador Windows, Acolhe, Acolhe PWA PT ES, Arquitetura e pastas, Conteúdo da publicação (+18 more)

### Community 7 - "Documentação e evidências 7"
Cohesion: 0.05
Nodes (37): 10.1 Pendências que não podem ser resolvidas apenas com arquivos, 10.2 Critério para declarar concluído, 10 Pendências e critérios de entrega, 11 Referências e rastreabilidade, 1 Visão geral e problema, 2.1 Jornada prevista, 2.2 Limites do MVP, 2 Escopo e experiência de uso (+29 more)

### Community 8 - "Objetos e treinamento Vision 8"
Cohesion: 0.06
Nodes (34): Vision pronta para dados, Baseline RAG agente, Pendências de entrega, COCO: auditoria e viabilidade de treino, COCO curadoria incompleta, Evidências obtidas, O que falta para um treino honesto, Uma foto verificada individualmente (+26 more)

### Community 9 - "Pipeline de integração 9"
Cohesion: 0.07
Nodes (32): environment, if, needs, permissions, runs-on, steps, APP_NAME, GH_TOKEN (+24 more)

### Community 10 - "Aplicação e interface 10"
Cohesion: 0.11
Nodes (24): api(), completed, connection(), copy, ensureSession(), lessons, local, openLesson() (+16 more)

### Community 11 - "Documentação e evidências 11"
Cohesion: 0.07
Nodes (28): 0min00s a 0min35s Problema e público, 0min35s a 1min10s Solução e uso, 1min10s a 2min05s MVP e inteligência artificial, 2min05s a 2min50s Indicadores e decisão, 2min50s a 3min30s Usuário e pagador, 3min30s a 4min10s Segurança e implementação, 4min10s a 4min40s Fechamento e próximos passos, Checklist antes de entregar (+20 more)

### Community 12 - "Objetos e treinamento Vision 12"
Cohesion: 0.11
Nodes (5): Handler, status(), GuardTests, VisionTests, reserve_output()

### Community 14 - "Pipeline de integração 14"
Cohesion: 0.09
Nodes (20): Experimento imagens Python, PYTHON_IMAGE, runs-on, steps, strategy, jobs, evaluate, base (+12 more)

### Community 15 - "Configuração do projeto 15"
Cohesion: 0.10
Nodes (20): build, cap_drop, environment, ports, read_only, restart, security_opt, tmpfs (+12 more)

### Community 16 - "Objetos e treinamento Vision 16"
Cohesion: 0.11
Nodes (17): names, 0, 1, 10, 11, 2, 3, 4 (+9 more)

### Community 17 - "Tutor e avaliação GenAI 17"
Cohesion: 0.17
Nodes (11): Análise técnica das respostas reais do Qwen 0.5B, Erros LLM reais observados, Erros reais observados e intervenção, Escolha final 1.5B — subconjunto pareado, sem benchmark completo, Execução inicial — antes da correção, Mitigação aplicada, Reteste estruturado, Smoke real do serviço (+3 more)

### Community 18 - "Tutor e avaliação GenAI 18"
Cohesion: 0.14
Nodes (12): Atualizar notebook 02 a partir de um relatório real já executado:, Comparação completa; pode demorar em CPU:, Contrato e avaliação, Estado verificado em 16/11/2026, GenAI: tutor bilíngue com modelo leve local, Modelo escolhido e limite de hardware, Preparar e executar, Próximas entregas (+4 more)

### Community 19 - "Documentação e evidências 19"
Cohesion: 0.17
Nodes (11): Aceitação com evidência, Arquivos para leitura, Atualizar o PDF, Documentação Acolhe, Documentação não substitui evidência, Publicação e cuidado com os arquivos, Checklist de aceite, Evidência rastreável (+3 more)

### Community 20 - "Infraestrutura e observabilidade 20"
Cohesion: 0.18
Nodes (10): summary, groups, name, rules, severity, alert, annotations, expr (+2 more)

### Community 21 - "Infraestrutura e observabilidade 21"
Cohesion: 0.18
Nodes (10): Alternativas oficiais avaliadas, Azure e observabilidade, DevSecOps Acolhe, ExecuÃ§Ã£o local, IaC Azure (exemplo real, NÃƒO aplicado), Observabilidade: quatro mÃ©tricas, PendÃªncias e roteiro de evidÃªncia, Pipeline (+2 more)

### Community 22 - "Infraestrutura e observabilidade 22"
Cohesion: 0.36
Nodes (10): azurerm_container_app.app, azurerm_container_app_environment.app, azurerm_resource_group.app, Terraform module: devsecops/terraform, output.url, provider.azurerm, var.image, var.location (+2 more)

### Community 23 - "Documentação e evidências 23"
Cohesion: 0.18
Nodes (10): Arquitetura de produto, Fora do escopo desta branch, GenAI: requisitos e decisões, Plano de execução e dependências, PRD — GenAI e Computer Vision, PRD GenAI Vision, Problema e objetivo, Riscos e critérios de conclusão (+2 more)

### Community 24 - "Pipeline de integração 24"
Cohesion: 0.18
Nodes (11): default, description, required, type, deploy, on, pull_request, push (+3 more)

### Community 25 - "Tutor e avaliação GenAI 25"
Cohesion: 0.20
Nodes (9): Base auditada e lacunas, Decisão de modelo final, Execução real qualidade pendente, Experimento e critérios, Fluxo do produto, Objetivo e escopo, Ordem de execução, PRD e plano de execução — GenAI (+1 more)

### Community 26 - "Configuração do projeto 26"
Cohesion: 0.20
Nodes (9): Dados privados fora do Git, Dataset examples only; do not publish photographs, annotations, or model weights, Documentation build dependencies and intermediate output, External snapshots: review redistribution rights before publishing, Python and local tooling, Rebuildable Graphify caches, machine paths and local Obsidian workspace, Runtime data and secrets, Runtime output; retain only the reviewed synthetic demo summary required by Docker (+1 more)

### Community 27 - "Infraestrutura e observabilidade 27"
Cohesion: 0.22
Nodes (8): global, scrape_interval, rule_files, scrape_configs, job_name, metrics_path, static_configs, targets

### Community 28 - "Infraestrutura e observabilidade 28"
Cohesion: 0.22
Nodes (8): pattern, rules, id, languages, message, pattern, pattern-either, severity

### Community 29 - "Documentação e evidências 29"
Cohesion: 0.22
Nodes (8): Ambiente e evidências, Escolha final: 1.5B leve em CPU, GenAI real: primeira execução, GenAI real: reteste e limite de aceitação, Mapa de conhecimento e revisão final, Testes e integração, Validação da branch GenAI/Vision — 16/11/2026, Vision: implementação versus execução

### Community 30 - "Indicadores e negócio 30"
Cohesion: 0.25
Nodes (7): Dados sintéticos e observados, Indicadores de uso, Indicadores disponíveis no relatório local, Indicadores do Acolhe, Indicadores propostos que exigem coleta adicional, Leitura de dados públicos, Perguntas para validar o negócio

### Community 31 - "Aplicação e interface 31"
Cohesion: 0.33
Nodes (6): translateVision(), visionButton, visionFile, visionForm, visionOutput, visionText()

### Community 32 - "Engenharia de dados 32"
Cohesion: 0.33
Nodes (5): Demanda por território, Serviços por território, Demanda por idioma, Razão ilustrativa demanda serviços, Proveniência e atualidade

### Community 33 - "Pipeline de integração 33"
Cohesion: 0.33
Nodes (5): CI e imagem Alpine, concurrency, cancel-in-progress, group, name

### Community 35 - "Tutor e avaliação GenAI 35"
Cohesion: 0.40
Nodes (4): Limite Qwen experimental, Reteste sem aprovação, Falhas semânticas e adversariais, Smoke serviço real PT ES

## Knowledge Gaps
- **211 isolated node(s):** `Autoridade acadêmica ausente`, `Manual PDF dez páginas`, `Texto e binários Git`, `Dados privados fora do Git`, `Demanda por território` (+206 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 441 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Acolhimento linguístico mediado` connect `Aplicação e interface 10` to `Documentação e evidências 7`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **What connects `Autoridade acadêmica ausente`, `Manual PDF dez páginas`, `Texto e binários Git` to the rest of the system?**
  _211 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Objetos e treinamento Vision 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06651017214397496 - nodes in this community are weakly interconnected._
- **Why does `jobs` connect `Pipeline de integração 9` to `Pipeline de integração 33`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Should `Tutor e avaliação GenAI 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05835010060362173 - nodes in this community are weakly interconnected._
- **Why does `Arquitetura modular local` connect `Robô e segurança 5` to `Objetos e treinamento Vision 0`, `Tutor e avaliação GenAI 1`, `Configuração do projeto 6`, `Documentação e evidências 7`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Should `Engenharia de dados 2` be split into smaller, more focused modules?**
  _Cohesion score 0.05585106382978723 - nodes in this community are weakly interconnected._

## Cobertura e custo honestos

AST local + anotações semânticas revisadas pela sessão; headings e referências literais complementam documentos. Contagens de tokens da sessão não estão expostas pela ferramenta: os zeros internos são placeholders e não significam custo zero. Não houve chamada de API de modelo externo. `docs/knowledge/coverage.json` distingue revisão semântica de indexação estrutural.

`graphify-out/` é saída local na árvore Git; escolha explicitamente quais artefatos compartilhar. O mapa descreve código e documentação, não comprova execução de modelos, infraestrutura ou requisitos acadêmicos.

### Alerta de integridade do extrator

Graphify relatou 231 referências a endpoints não declarados na extração e 101 relações colapsadas por par na projeção não direcionada (em especial chaves YAML repetidas). Referências externas e resolução AST têm limites; o mapa pode ser incompleto. A extração bruta permanece em `.graphify_extract.json`; não use ausência de aresta como prova de ausência de dependência.
