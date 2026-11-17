# Checklist de entregáveis por disciplina (GS 2026.2)

Rodado de novo em 17/11 à noite, contra o enunciado "Desafio FIAP GS CitizenTech 4ES", na branch `Aksel+Ian`. Prazo: 19/11 às 23h55, no Teams de cada disciplina, um envio por equipe. Repositório, aplicação e vídeos precisam continuar públicos e no ar durante a correção, que leva até uma semana.

Legenda: ✅ atende · 🟡 parcial · ❌ falta · 👤 só a equipe pode fazer (gravar, enviar, hardware)

Verificações automáticas nesta rodada: 132 testes Python e 21 testes de interface aprovados; Gitleaks, Semgrep, Trivy (IaC), `terraform fmt` e `promtool test rules` sem achados; GitHub Actions verde em todos os pushes da branch. MVP público, repositório e branch respondem HTTP 200.

Links: repositório https://github.com/Acolhe-Projeto/Acolhe---GS8 (branch Aksel+Ian) · MVP https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io

PDFs prontos em `docs/entregas/`: `GS_BigData_Acolhe.pdf`, `GS_RPA_Acolhe.pdf`, `GS_DevSecOps_Acolhe.pdf` (regerar com `python docs/entregas/gerar_pdfs.py`; prints em `docs/entregas/prints/`).

## 1. Big Data Architecture & Data Integration (Ian e Aksel)
Entrega: PDF com o link do repositório (`GS_BigData_Acolhe.pdf`, 9 páginas, na ordem pedida).

| Requisito | Status | Evidência |
|---|---|---|
| 01 Duas fontes, uma externa real | ✅ | IBGE e OBMigra, coletados em 07, 14 e 17/11; `amostras/`. |
| 02 DAG agendado grava em `chegada/` com data no nome | ✅ | `acolhe_official_snapshots` (04:00 UTC) → `chegada/<fonte>/<nome>_AAAA-MM-DD.csv`; rodou com sucesso no Airflow real. |
| 03 Paralelismo, conferência, notificação, Variables | ✅ | Graph mostra `coletar_ibge` ∥ `coletar_obmigra` → `conferir_chegada`; `chegada_ok` e `task_failure` (falha provocada) registrados; endpoints em Variables. |
| 04 Dois lotes de dias diferentes no Volume | ✅ | Lotes reais de 14/11 e 17/11 enviados por dia de coleta. O enunciado diz "pela interface": o envio foi pela CLI oficial, porque o Databricks bloqueia automação do navegador. |
| 05 Bronze incremental, contagens antes/depois | ✅ | Execução limpa: bronze_municipios 0 → 645 → 1290 → 1290; DESCRIBE HISTORY sem versão nova na reexecução. |
| 06 Prata com MERGE e 3 regras com contagem | ✅ | Tabela `quality_rules`: R1/R2/R3 = 1/1/1 no lote de teste de qualidade; M1–M3 e O1–O3 = 0 nos dados reais. |
| 07 Ouro dimensional, 5 consultas, uma de impacto | ✅ | 8 consultas com resultado e interpretação; a 6 é a de impacto. |
| 08 LGPD na Ouro e tela do MVP | ✅ | Sem dado pessoal, chaves em hash; print do painel do MVP público. |
| 09 README e organização | ✅ | `big_data/README.md` com integrantes e tabela dos requisitos. |
| Prints do Airflow (Graph e Grid) | ✅ | No PDF, seção 5. |
| Prints da interface do Databricks | 🟡 👤 | Evidência por tabelas e consultas via API. Prints da UI (Catalog, job runs) ficam com a equipe: salve como `docs/entregas/prints/databricks_*.png` e rode `gerar_pdfs.py`, que os inclui sozinho. |
| Envio no Teams | 👤 | |

## 2. Robotic Process Automation (Ian e Aksel)
Entrega: PDF com BPMN, PDD, evidências e links (`GS_RPA_Acolhe.pdf`) e vídeo de até 3 min.

| Etapa | Status | Evidência |
|---|---|---|
| 01 Mapeamento (PDD e BPMN) | ✅ | BPMN renderizado no PDF; PDD no README e no PDF. |
| 02 Automação em Python no GitHub | ✅ | `rpa/robot.py`. |
| 03 Decisão e repetição | ✅ | Regra de reforço (< 60% com ≥ 3 tentativas); laço sobre cada tentativa. |
| 04 Exceções e resiliência | ✅ | Banco ausente, esquema inválido, banco ocupado, dados duplicados/inconsistentes. |
| 05 Logs e auditoria | ✅ | `rpa/logs/` com sucesso, decisão e falha, sem IDs. |
| 06 Integração com o MVP | ✅ | Print do painel "Acompanhamento automático" com a decisão. |
| 07 Testes de sucesso, decisão e falha | ✅ | Tabela no PDF; `demo_e2e.py` e testes na esteira. |
| 08 README estruturado | ✅ | Integrantes, PDD, BPMN, instruções. |
| Vídeo de até 3 min | ❌ 👤 | Roteiro em `docs/roteiros_videos.md`. O PDF tem um campo vermelho "inserir o link do vídeo": regere com `VIDEO_RPA=<link> python docs/entregas/gerar_pdfs.py`. |

## 3. Secure DevOps Tools & Cloud Computing (Ian e Aksel), 14 pontos
Entrega: PDF único com links clicáveis (`GS_DevSecOps_Acolhe.pdf`), no portal da disciplina.

| Critério | Status | Evidência |
|---|---|---|
| Dockerfile enxuto, não root, sem segredo, compose sobe | ✅ | Trivy 0 HIGH/CRITICAL; `persistence_check.sh`. |
| Terraform, state e tfvars fora do repo, sem porta admin aberta | ✅ | 8 recursos em canadacentral; só ingress HTTPS. |
| Actions a cada push com build, Gitleaks, Semgrep e Trivy | ✅ | Workflow em todo push; runs verdes na branch. |
| Segredos em GitHub Secrets e deploy automático | ✅ / 🟡 | OIDC, environment `production`, secrets e `DEPLOY_ENABLED=true` configurados. O primeiro deploy pela `main` só acontece depois do merge; nesse momento é preciso tornar público o pacote GHCR da organização e rodar o job de novo (o job falha antes de tocar no Azure se o pacote estiver privado). |
| Execução barrada e a corrigida | ✅ | Runs 44190586981 (vermelho) e 44191227009 (verde), prints no PDF. |
| Dashboard das 4 métricas e alerta disparado | ✅ | Grafana apontando para a URL pública; `AcolheUnavailable` em FIRING no ensaio com o container local parado (identificado como `local-drill`). |
| Diagrama, responsabilidade compartilhada, LGPD, custo, README | ✅ | No PDF e no `devsecops/README.md`. |
| URL pública e Ficha Técnica no README | ✅ | Ficha Técnica atualizada com a infraestrutura em produção. |
| Envio no portal | 👤 | |

## 4. Generative AI for Engineering (Rony)
| Item | Status | Situação |
|---|---|---|
| Testes com gabarito e "não consta"; base com fonte | 🟡 | 16 perguntas e corpus com fontes em `genai/`. |
| recall@1/@3 com limiar justificado | 🟡 | 0,6875 medido; falta justificar o limiar. |
| Geração fundamentada (JSON, citação, recusa) | ❌ | LLM local nunca executado; `02_local_llm.ipynb` sem saída. |
| LoRA ou agente vs RAG; placar das 3 configurações | ❌ | `compare.py` existe e não foi executado com modelo. |
| 5 erros reais do modelo | 🟡 | Os 5 documentados são do buscador. |
| Estrutura `notebooks/ base/ avaliacao/` e integrantes no README | 🟡 | Estrutura diferente; README sem RMs. |

## 5. Applied Computer Vision (Rony)
| Item | Status | Situação |
|---|---|---|
| Treino customizado e inferência | ❌ | Sem dataset licenciado, anotação ou modelo treinado. |
| Repositório documentado | 🟡 | `vision/README.md`, `train.py`. |
| PDF (resumo de 250 palavras, objetivo de 50) e vídeo | ❌ 👤 | |

## 6. Business Intelligence & Startup Development (Tomáz)
| Item | Status | Situação |
|---|---|---|
| Vídeo pitch de até 5 min com o MVP real na URL pública | 👤 | A URL pública está no ar e mostra os dados oficiais (75.600 pedidos de refúgio, 16% crianças), úteis como "dado que prova a dor". Roteiro em `bi/roteiro_pitch.md`. |

## 7. Project-Based Maker Lab (Tomáz)
| Item | Status | Situação |
|---|---|---|
| Robô com sensor adicional e IA | 🟡 👤 | PR #2: firmware, DHT11, gestos e voz local, com testes. Falta o vídeo com o robô físico. |
| README e vídeo de até 6 min | 🟡 👤 | `robot/README.md` com integrantes; vídeo pendente. |

## Para todos, antes de 19/11 às 23h55
- Abrir e mesclar o PR da `Aksel+Ian` na `main`; a branch já contém a `main` atual e a CI está verde.
- Depois do merge: tornar público o pacote `ghcr.io/acolhe-projeto/acolhe---gs8` e rodar o job de deploy de novo.
- Manter o Azure, o pacote GHCR e os vídeos públicos até o fim da correção (cerca de 26/11).
- Parar o Grafana local depois dos prints (`docker compose -f devsecops/monitoring/public/compose.yaml down`), para o app voltar a escalar a zero.
