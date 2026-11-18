# Checklist de entregáveis por disciplina (GS 2026.2)

## Rodada de 18/11 (madrugada)
- PR #3 (`Aksel+Ian`) foi mesclado na `main` (commit `30af065`). A `main` agora tem Big Data, RPA, DevSecOps e Maker, com conteúdo idêntico ao que passou na CI.
- CI da `main` (run 44210859059): `test-and-build` verde. O job `deploy` parou em "Verify image is publicly pullable" porque o pacote GHCR da organização era privado (só um owner pode torná-lo público); o Azure não foi tocado. Correção: registro privado no Azure (ACR) com identidades gerenciadas, criado por Terraform; o deploy automático passa a enviar a imagem para lá.
- Rony avançou na branch `feat/genai-vision`, ainda fora da `main`: LLM local Qwen2.5 3B, comparação baseline × RAG/agente (7/16 contra 14/16 no D16), `genai/base/`, `genai/avaliacao/` e relatório; Vision com modelo YOLO treinado, relatório, PDF e vídeos (GenAI https://youtu.be/csoYGnIeviM, Vision https://youtu.be/8FPF_BkSh58). Essa branch partiu de uma `main` antiga e tem conflito com a atual em 7 arquivos (README, `app/server.py`, `app.js`, `index.html`, `style.css`, `.gitignore`, `Iniciar-Acolhe.cmd`); precisa de merge com resolução antes de 19/11.

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
| Segredos em GitHub Secrets e deploy automático | ✅ | OIDC, environment `production`, secrets e variáveis configurados. O primeiro deploy pela `main` parou na proteção, porque o pacote GHCR da organização era privado e só um owner pode torná-lo público. A imagem passou a ir para um Azure Container Registry privado (`AcrPush` para a CI, `AcrPull` para o app), aplicado por Terraform em 18/11. |
| Execução barrada e a corrigida | ✅ | Runs 44190586981 (vermelho) e 44191227009 (verde), prints no PDF. |
| Dashboard das 4 métricas e alerta disparado | ✅ | Grafana apontando para a URL pública; `AcolheUnavailable` em FIRING no ensaio com o container local parado (identificado como `local-drill`). |
| Diagrama, responsabilidade compartilhada, LGPD, custo, README | ✅ | No PDF e no `devsecops/README.md`. |
| URL pública e Ficha Técnica no README | ✅ | Ficha Técnica atualizada com a infraestrutura em produção. |
| Envio no portal | 👤 | |

## 4. Generative AI for Engineering (Rony)
Situação conforme a branch `feat/genai-vision`, ainda não mesclada na `main`; o professor só vê o que estiver na branch padrão.

| Item | Status | Situação |
|---|---|---|
| Testes com gabarito, base com fonte, estrutura `base/ avaliacao/ notebooks/` | 🟡 | Na branch: `genai/base/` (corpus, fontes, manifest), `genai/avaliacao/` (conjuntos A a D), 3 notebooks. |
| LLM local, geração fundamentada e recusa | 🟡 | Na branch: Qwen2.5 3B via Ollama, relatórios de execução e smoke do serviço. |
| Comparação baseline × RAG × agente | 🟡 | Na branch: 7/16 contra 14/16 no conjunto D16, em `docs/entregas/GENAI_RELATORIO.md`. |
| Vídeo e relatório | 🟡 | Vídeo https://youtu.be/csoYGnIeviM; relatório na branch. |
| Merge na `main` | ❌ | Conflito em 7 arquivos com a `main` atual. |

## 5. Applied Computer Vision (Rony)
| Item | Status | Situação |
|---|---|---|
| Treino customizado e inferência | 🟡 | Na branch: checkpoint YOLO avaliado, curvas PR e matriz de confusão, `vision/reproduce.py`. |
| PDF e vídeo | 🟡 | `docs/ACOLHE_VISION.pdf` e https://youtu.be/8FPF_BkSh58 na branch. |
| Merge na `main` | ❌ | Mesmo conflito da branch `feat/genai-vision`. |

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
- ✅ PR da `Aksel+Ian` mesclado na `main` (PR #3).
- ✅ Deploy automático pelo Azure Container Registry: não depende mais de pacote público no GHCR.
- Mesclar `feat/genai-vision` na `main`, resolvendo os 7 conflitos, para GenAI e Vision aparecerem na branch padrão.
- Manter o Azure, o pacote GHCR e os vídeos públicos até o fim da correção (cerca de 26/11).
- Parar o Grafana local depois dos prints (`docker compose -f devsecops/monitoring/public/compose.yaml down`), para o app voltar a escalar a zero.
