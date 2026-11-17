# Checklist de entregáveis por disciplina (GS 2026.2)

Conferido em 2026-11-17 contra o enunciado "Desafio FIAP GS CitizenTech 4ES" e a branch `Aksel+Ian`. Prazo de todas as disciplinas: 19/11 às 23h55, no Teams de cada uma, com um envio por equipe. Repositório, aplicação e vídeos precisam continuar públicos e no ar durante a correção, que leva até uma semana depois do prazo.

Legenda: ✅ atende · 🟡 parcial · ❌ falta · 👤 só a equipe pode fazer (gravar, enviar, montar PDF, hardware)

Links que valem para todas: repositório https://github.com/Acolhe-Projeto/Acolhe---GS8 (movido de TomazVC em 17/11; branch Aksel+Ian, ainda sem merge na main) · MVP https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io

## 1. Big Data Architecture & Data Integration (Ian e Aksel)
Entrega: PDF com o link do repositório.

| Requisito | Status | Situação |
|---|---|---|
| 01 Duas fontes, uma externa real | ✅ | API de Localidades do IBGE e relatório OBMigra 2025, coletados em 3 dias reais (07, 14 e 17/11), além das fontes demonstrativas `demand` e `services`. |
| 02 DAG agendado grava em `chegada/`, um arquivo por coleta com a data no nome | 🟡 | O DAG `acolhe_official_snapshots` está agendado (04:00 UTC) e rodou no Airflow real, mas grava em `official_snapshots/raw/<fonte>/<sha256>` com a data no manifesto. Falta a pasta `chegada/` com a data no nome do arquivo. |
| 03 Duas tarefas paralelas, uma tarefa que confere a chegada, chaves em Variables | 🟡 | O paralelismo está comprovado (IBGE e OBMigra ao mesmo tempo). Falta uma tarefa `conferir_chegada` e notificação de falha (etapa 2 do enunciado). As fontes não usam chave, então basta dizer isso no relatório. |
| 04 Dois lotes no Volume, de dias de coleta diferentes | 🟡 | Os lotes do Volume são os CSV demonstrativos de 05/11 e 06/11 (data do dado). Os arquivos reais coletados em dias diferentes ainda não entram como lotes da Bronze. O enunciado também pede upload "pela interface"; usamos o notebook `00_setup_volume`. |
| 05 Bronze com COPY INTO, sem duplicar, contagens antes e depois | ✅ | 14/11: bronze 4 → 8 → 8. 17/11: nova execução em outro dia real sem nenhum arquivo novo carregado (ver `big_data/evidence/databricks_20261117.md`). |
| 06 Prata: tipos, nulos, MERGE e 3 regras de qualidade com total barrado por regra | 🟡 | Tipos, MERGE e quarentena prontos. O pipeline local grava o motivo de cada rejeição, mas o notebook Databricks não mostra o total barrado por cada uma das 3 regras. |
| 07 Ouro: 1 fato, 2 dimensões, 5 consultas, uma de impacto | ✅ | `fact_indicators`, `dim_region`, `dim_language`, `dim_municipality`, `gold_official_context`; 8 consultas interpretadas em `EVIDENCIAS.md`. Consulta 6 (cerca de 12.096 crianças solicitantes de refúgio) é a de impacto. |
| 08 LGPD na Ouro e tela do MVP | 🟡 | A Ouro não tem dado pessoal e as dimensões no Databricks usam hash SHA-256. O MVP consome `summary.json` em `/api/gold` (painel "Território e acolhimento"). Falta escrever isso no relatório com o print da tela. |
| 09 README com integrantes, arquitetura e passo a passo | 🟡 | Arquitetura e passo a passo prontos; o README de `big_data/` não lista os integrantes com RM. A pasta `amostras/` sugerida não existe (`databricks/data/` cumpre o papel). |
| PDF na ordem pedida (9 itens, prints do Airflow Graph e Grid) | 👤 | Prints em http://localhost:8081 com o Airflow no ar no WSL. |

## 2. Robotic Process Automation (Ian e Aksel)
Entrega: PDF (BPMN, PDD, evidências, links) e vídeo de até 3 minutos.

| Etapa | Status | Situação |
|---|---|---|
| 01 Mapeamento (PDD e fluxo) | ✅ | PDD no `rpa/README.md`; `processo.bpmn` com gateway de decisão, abre no bpmn.io. |
| 02 Automação em Python no GitHub | ✅ | `rpa/robot.py`. |
| 03 Decisão e repetição | ✅ | Regra: lição com menos de 60% de acerto e pelo menos 3 tentativas vai para revisão. Laços sobre lições e idiomas, mais o `--every`. |
| 04 Exceções e resiliência | 🟡 | Banco ausente e esquema inválido tratados e logados. O enunciado também cita dados duplicados ou inconsistentes, e o robô não trata isso. |
| 05 Logs com data/hora, itens, sucessos e falhas | ✅ | `robot.log` com `report_started`, `decision`, `report_completed` e `report_failed`. O `.gitignore` ignora `*.log`, então nenhuma amostra de log foi para o GitHub (pasta `logs/` sugerida). |
| 06 Integração com o MVP | ✅ | `/api/automation` alimenta o painel "Acompanhamento automático" com totais e decisão. |
| 07 Testes de sucesso, decisão e falha | ✅ | `rpa/demo_e2e.py` e 8 testes; evidência em `rpa/evidence/`. |
| 08 README estruturado | 🟡 | Falta a lista de integrantes com RM no `rpa/README.md`. |
| PDF e vídeo de até 3 min | 👤 | Roteiro pronto em `docs/roteiros_videos.md`. |

## 3. Secure DevOps Tools & Cloud Computing (Ian e Aksel), 14 pontos
Entrega: PDF único com links clicáveis, no portal da disciplina.

| Critério | Status | Situação |
|---|---|---|
| Dockerfile enxuto, não root, sem segredo, compose sobe | ✅ | Alpine fixada por digest, UID 10001, Trivy 0 HIGH/CRITICAL, `persistence_check.sh`. |
| Terraform, state e tfvars fora do repo, sem porta admin aberta | ✅ | 8 recursos criados em canadacentral; state e tfvars ficam só no WSL; só o ingress HTTPS 443 é público. |
| Actions com build, Gitleaks, Semgrep e Trivy a cada push | 🟡 | Tudo verde no run 43548910363, mas o workflow só dispara em push na `main` e em PR. O enunciado pede a cada push. |
| Segredos em GitHub Secrets e deploy automático | 🟡 | O job de deploy existe, mas um administrador do repositório (Tomáz) precisa configurar o OIDC e os secrets. Até lá, o deploy é feito pelo Terraform. |
| Execução barrada e a corrigida | 🟡 | Barradas reais na verificação local (Semgrep exec(), Trivy CRITICAL no storage, Trivy 0.60 no Dockerfile.candidate). Ainda não existe um run vermelho no GitHub seguido do verde. |
| Dashboard com as 4 métricas de ouro e um alerta disparado | 🟡 | Sinais medidos e alerta `AcolheUnavailable` disparado no Prometheus. O dashboard do Grafana existe em JSON, mas nunca foi aberto num Grafana de verdade, e o enunciado pede o print. |
| Diagrama, responsabilidade compartilhada, LGPD, custo, README | ✅ | Seções no `devsecops/README.md`. O diagrama é texto; uma imagem fica melhor no PDF. |
| URL pública e Ficha Técnica no README | ✅ | URL no ar; "Ficha técnica" no README raiz. |
| PDF único | 👤 | |

## 4. Generative AI for Engineering (Rony)
Entrega: links do repositório. Relatório no GitHub.

| Item | Status | Situação |
|---|---|---|
| Casos de teste com gabarito, incluindo "não consta" | 🟡 | 16 perguntas manuais em `genai/`. |
| Base em trechos com fonte | ✅ | `genai/data/corpus.json`. |
| recall@1 e recall@3 com limiar justificado | 🟡 | 0,6875 nos dois; falta justificar o limiar. |
| Geração fundamentada (JSON, citação, recusa) | ❌ | O LLM local nunca rodou (Ollama bloqueado); `02_local_llm.ipynb` está sem saída. |
| LoRA ou agente comparado ao RAG, placar das 3 configurações | ❌ | `compare.py` existe e nunca foi executado com modelo. |
| 5 erros reais com correção | 🟡 | Os 5 documentados são erros do buscador, e o enunciado pede erros do modelo. |
| Estrutura `notebooks/ base/ avaliacao/`, README com integrantes | 🟡 | Estrutura diferente; README sem RMs. |

## 5. Applied Computer Vision (Rony)
| Item | Status | Situação |
|---|---|---|
| Treino customizado de detecção | ❌ | Estrutura pronta, mas sem dataset licenciado, sem anotação e sem modelo treinado. |
| Repositório documentado | 🟡 | `vision/README.md` e `train.py` existem. |
| PDF (resumo de 250 palavras, objetivo de 50) e vídeo | 👤 ❌ | |

## 6. Business Intelligence & Startup Development (Tomáz)
| Item | Status | Situação |
|---|---|---|
| Vídeo pitch de até 5 min, equipe aparecendo, MVP real na URL pública, YouTube não listado | 👤 | A URL pública agora existe. Roteiro em `bi/roteiro_pitch.md`. Os indicadores atuais são demonstrativos. Os dados reais do OBMigra (75.600 pedidos, 16% crianças) servem como "dado que prova a dor" no 0:00 do roteiro. |

## 7. Project-Based Maker Lab (Tomáz)
| Item | Status | Situação |
|---|---|---|
| Robô com sensor adicional integrado à IA | 🟡 👤 | PR #2 na main (17/11): firmware `acolhe.ino`, sensor DHT11, gestos, voz local (`robot/voice.py`, `hardware.py`) e testes. Falta comprovar com o robô físico em vídeo. |
| README com componentes, instalação e integração | 🟡 | `robot/README.md` com integrantes e RMs. |
| Vídeo de até 6 min | 👤 | Roteiro em `docs/roteiros_videos.md`. |

## Para todos
- Fazer o merge da `Aksel+Ian` na `main` antes de 19/11, porque o professor vai abrir a branch padrão. A `main` recebeu o PR #2 (Maker) depois que a branch foi criada: o merge tem um conflito em `app/server.py`, e o resto (`.gitignore`, `app.js`, `roteiros_videos.md`) se resolve sozinho.
- Na organização Acolhe-Projeto, a conta Oslyanka agora é administradora, então os secrets do deploy automático (OIDC Azure) já podem ser configurados.
- Não derrubar o Azure nem tornar privado o pacote GHCR até o fim da correção (cerca de 26/11).
- Cada PDF precisa de nome completo e RM de todos; a falta disso tira 0,5 em Big Data.
