# Checklist de entregáveis por disciplina (GS 2026.2)

Rodada de 18/11, na `main` (`22af14f`), contra o enunciado "Desafio FIAP GS CitizenTech 4ES". Prazo: 19/11 às 23h55, um envio por equipe em cada disciplina. Repositório, aplicação e vídeos precisam continuar públicos e no ar durante a correção (até cerca de 26/11).

Atualização de links em 19/11: RPA, BI e Maker já estão vinculados no README. As verificações da rodada de 18/11 abaixo são históricas; esta atualização não reavalia o conteúdo dos vídeos de RPA e BI.

Legenda: ✅ atende · 🟡 parcial · ❌ falta · 👤 só a equipe pode fazer (gravar, enviar, hardware)

Conferido nesta rodada:
- Repositório público, HTTP 200 sem login: https://github.com/Acolhe-Projeto/Acolhe---GS8
- MVP público, `/api/health` = `ok`: https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io
- Vídeos de GenAI e Vision respondem no YouTube.
- Últimos 3 runs da `main` verdes (testes, Gitleaks, Semgrep, Trivy, deploy no ACR e health check). Nenhum PR aberto.
- Nenhum e-mail pessoal em arquivo versionado.

O que enviar em cada disciplina está em [docs/entregas/README.md](entregas/README.md).

## Resumo

| Disciplina | Responsável | Pronto para enviar? | Falta |
|---|---|---|---|
| Big Data | Ian e Aksel | ✅ | Só o envio |
| DevSecOps | Ian e Aksel | ✅ | Só o envio no portal |
| GenAI | Rony | ✅ | Só o envio |
| Vision | Rony | ✅ | Só o envio |
| RPA | Ian e Aksel | ✅ 👤 | PDF atualizado com vídeo de 2min50s e link da main; falta o envio |
| BI | Tomáz | 🟡 👤 | Link publicado; conferir duração, acesso e requisitos do pitch |
| Maker | Tomáz | 🟡 👤 | Vídeo e link publicados; limites em `docs/maker-entrega.md` |

## 1. Big Data Architecture & Data Integration (Ian e Aksel)
Entrega: PDF com o link do repositório, `docs/entregas/GS_BigData_Acolhe.pdf` (12 páginas).

| Requisito | Status | Evidência |
|---|---|---|
| 01 Duas fontes, uma externa real | ✅ | IBGE e OBMigra, coletados em 07, 14 e 17/11; `big_data/amostras/`. |
| 02 DAG agendado grava em `chegada/` com data no nome | ✅ | `acolhe_official_snapshots` (04:00 UTC) → `chegada/<fonte>/<nome>_AAAA-MM-DD.csv`. |
| 03 Paralelismo, conferência, notificação, Variables | ✅ | `coletar_ibge` ∥ `coletar_obmigra` → `conferir_chegada`; `chegada_ok` e `task_failure` registrados; endpoints em Variables. |
| 04 Dois lotes de dias diferentes no Volume | ✅ | Lotes de 14/11 e 17/11. Envio pela CLI oficial, porque o Databricks bloqueia automação do navegador. |
| 05 Bronze incremental, contagens antes/depois | ✅ | bronze_municipios 0 → 645 → 1290 → 1290; reexecução sem versão nova no DESCRIBE HISTORY. |
| 06 Prata com MERGE e 3 regras com contagem | ✅ | `quality_rules`: R1/R2/R3 = 1/1/1 no lote de teste; regras dos dados reais = 0. |
| 07 Ouro dimensional, 5 consultas, uma de impacto | ✅ | 8 consultas com interpretação; a 6 é a de impacto. |
| 08 LGPD na Ouro e tela do MVP | ✅ | Sem dado pessoal, chaves em hash; print do painel do MVP. |
| 09 README e organização | ✅ | `big_data/README.md` com integrantes e tabela dos requisitos. |
| Prints do Airflow e do Databricks | ✅ | Graph, Grid e 6 prints da interface do Databricks, com e-mail e ID ocultados. |
| Envio | 👤 | |

## 2. Robotic Process Automation (Ian e Aksel)
Entrega: PDF com BPMN, PDD, evidências e links (`docs/entregas/GS_RPA_Acolhe.pdf`, 4 páginas) e vídeo de até 3 min.

| Etapa | Status | Evidência |
|---|---|---|
| 01 Mapeamento (PDD e BPMN) | ✅ | BPMN renderizado no PDF; PDD no `rpa/README.md` e no PDF. |
| 02 Automação em Python no GitHub | ✅ | `rpa/robot.py`. |
| 03 Decisão e repetição | ✅ | Reforço quando < 60% com ≥ 3 tentativas; laço por tentativa. |
| 04 Exceções e resiliência | ✅ | Banco ausente, esquema inválido, banco ocupado, dados inconsistentes. |
| 05 Logs e auditoria | ✅ | `rpa/logs/` com sucesso, decisão e falha, sem IDs. |
| 06 Integração com o MVP | ✅ | Painel "Acompanhamento automático" no app. |
| 07 Testes de sucesso, decisão e falha | ✅ | `rpa/demo_e2e.py` e testes na esteira. |
| 08 README estruturado | ✅ | Integrantes, PDD, BPMN, instruções. |
| Vídeo de até 3 min | ✅ | https://youtu.be/9Vxrja0XkZk, 2min50s; link incluído no PDF. O gerador utiliza esse vídeo por padrão. |

## 3. Secure DevOps Tools & Cloud Computing (Ian e Aksel), 14 pontos
Entrega: PDF único com links clicáveis (`docs/entregas/GS_DevSecOps_Acolhe.pdf`, 6 páginas), no portal da disciplina.

| Critério | Status | Evidência |
|---|---|---|
| Dockerfile enxuto, não root, sem segredo, compose sobe | ✅ | Trivy 0 HIGH/CRITICAL; `persistence_check.sh`. |
| Terraform, state e tfvars fora do repo, sem porta admin aberta | ✅ | Container Apps em canadacentral, ACR privado, só ingress HTTPS. |
| Actions a cada push com build, Gitleaks, Semgrep e Trivy | ✅ | Runs verdes na `main`. |
| Segredos em GitHub Secrets e deploy automático | ✅ | OIDC com subject imutável; push na `main` → ACR → Container App → health check. |
| Execução barrada e a corrigida | ✅ | Runs 44190586981 (vermelho) e 44191227009 (verde), com prints. |
| Dashboard das 4 métricas e alerta disparado | ✅ | Grafana na URL pública; `AcolheUnavailable` em FIRING no ensaio. |
| Diagrama, responsabilidade compartilhada, LGPD, custo, README | ✅ | No PDF e em `devsecops/README.md`. |
| URL pública e Ficha Técnica no README | ✅ | Seção "Ficha técnica" do README principal. |
| Envio no portal | 👤 | |

## 4. Generative AI for Engineering (Rony)
| Item | Status | Evidência |
|---|---|---|
| Base com fonte e testes com gabarito (`base/ avaliacao/ notebooks/`) | ✅ | `genai/base/`, `genai/avaliacao/` (conjuntos A a D), 3 notebooks. |
| LLM local, resposta fundamentada e recusa | ✅ | Qwen2.5 3B via Ollama; relatórios de execução. |
| Comparação baseline × RAG/agente | ✅ | 7/16 contra 14/16 no D16, em `docs/entregas/GENAI_RELATORIO.md`. |
| Relatório e vídeo | ✅ | Relatório com integrantes; vídeo https://youtu.be/csoYGnIeviM. |
| Envio | 👤 | |

## 5. Applied Computer Vision (Rony)
| Item | Status | Evidência |
|---|---|---|
| Treino customizado e inferência | ✅ | Checkpoint YOLO avaliado, curvas PR, matriz de confusão, `vision/reproduce.py`, rota `/api/vision/predict`. |
| PDF e vídeo | ✅ | `docs/ACOLHE_VISION.pdf` (6 páginas) e https://youtu.be/8FPF_BkSh58. |
| Envio | 👤 | |

## 6. Business Intelligence & Startup Development (Tomáz)
| Item | Status | Situação |
|---|---|---|
| Vídeo pitch de até 5 min, YouTube não listado, equipe aparecendo, MVP na URL pública | 🟡 👤 | Link fornecido pela equipe: https://youtu.be/MRKXTSPRdXA. Conferir duração, acesso e conteúdo antes do envio. Roteiro em `bi/roteiro_pitch.md`. |

## 7. Project-Based Maker Lab (Tomáz)
| Item | Status | Situação |
|---|---|---|
| Robô com sensor adicional e IA | 🟡 👤 | Montagem, LCD, conversa ambiental e treino no vídeo https://youtu.be/Bm3uaAx4McE. Limites em `docs/maker-entrega.md`. |
| README e vídeo de até 6 min | 🟡 👤 | Vídeo de 4min13s vinculado no README; falha e oferta automática por calor não identificadas no vídeo, conforme `docs/maker-entrega.md`. |

## Para todos, antes de 19/11 às 23h55
- Conferir duração, acesso e requisitos dos vídeos já vinculados no README; no RPA, conferir o link no PDF e regerar se necessário.
- Um integrante envia por disciplina, com os quatro nomes e RMs.
- Manter o Azure (Container App e ACR) e os vídeos públicos até o fim da correção (cerca de 26/11).
- Parar o Grafana local depois dos prints (`docker compose -f devsecops/monitoring/public/compose.yaml down`), para o app voltar a escalar a zero.
