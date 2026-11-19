# DevSecOps Acolhe

## Integrantes
- Tomáz Versolato Carballo, RM 551417
- Rony Ken Nagai, RM 551549
- Aksel Viktor Caminha Rae, RM 99011
- Ian Xavier Kuraoka, RM 98860


## Execução local
Na raiz, `python -m app.server` inicia a aplicação (porta 8080). `docker compose up --build` é o caminho container. `docker compose --profile monitoring up --build` acrescenta Prometheus em http://localhost:9090. A aplicação fica restrita ao loopback do host na porta 8080. Container não root, filesystem somente leitura no Compose, capabilities removidas e no-new-privileges. Build, smoke HTTP/SQLite e execução com UID 10001 foram verificados em WSL2/Docker e na CI, conforme as evidências abaixo.

## Histórico: execução nativa verificada (2026-11-14 UTC, Windows 11)
Ferramentas portateis, mesmas versoes da CI quando ha binario Windows: Terraform 1.17.2, Gitleaks 8.24.2, Prometheus/promtool 3.2.1, Node 22.23.5, Trivy 0.76.1 (o binario Windows da 0.60.0 nao existe mais; hash conferido com o checksums oficial), Semgrep 1.185.0 (1.111.0 nao suporta Windows).

| Verificacao | Resultado |
|---|---|
| `python -B -m unittest discover` | todos aprovados (ver VERIFICATION) |
| `node --check` + `node --test tests/frontend.test.cjs` | 11/11 |
| `terraform fmt -check`, `init -backend=false`, `validate` | ok / valido |
| `trivy config .` HIGH/CRITICAL (Dockerfile, Dockerfile.candidate, Terraform) | 0 achados |
| `gitleaks dir .` | nenhum vazamento |
| `semgrep --config devsecops/semgrep.yml app robot rpa big_data` | 0 achados apos excecao revisada (abaixo) |
| `promtool check config/rules` + `promtool test rules alerts.test.yml` | SUCCESS (3 cenarios) |

**Execucao barrada e corrigida (local).** Ao ampliar o escopo do Semgrep para `rpa` e `big_data`, a regra `no-dynamic-evaluation` barrou um `exec()` real em `big_data/test_copy_statement.py`. Era o teste executando o AST do proprio notebook contra um stub, sem entrada externa; recebeu excecao revisada `nosemgrep` com justificativa, sem retirar a pasta do scan. Ensaio adicional: arquivo com `eval()` e token no formato GitHub -> semgrep exit 1 e gitleaks exit 1 (BLOQUEADO); arquivo removido -> ambos exit 0 (APROVADO). A evidência oficial no GitHub foi registrada em 17/11: os links da execução barrada e da corrigida estão na seção seguinte.

**Quatro sinais de ouro ao vivo.** App + Prometheus 3.2.1 nativos, 70 s de carga (6 clientes, 12.708 requisicoes reais incluindo tentativas do quiz). Consultas PromQL: latencia media 0,015 s; trafego 174 req/s; erros 0; saturacao 1 requisicao ativa. Essa leitura revelou um defeito: o proprio scrape de `/metrics` contava como requisicao ativa, logo a saturacao nunca chegava a 0. Corrigido em `app/server.py` com teste `test_metrics_four_golden_signals_idle_saturation_is_zero`.

**Alerta disparado.** Com o app parado, `AcolheUnavailable` passou de inactive -> pending -> firing no Prometheus real (ver VERIFICATION para horarios). Sem Alertmanager: o alerta aparece em `/alerts` do Prometheus; nenhuma mensagem e enviada.

**Persistencia corrigida.** O banco ficava em `/tmp` (tmpfs) e se perdia a cada recriacao. Agora `ACOLHE_DB=/data/acolhe.db`, diretorio `/data` do UID 10001 e volume nomeado `acolhe-data` no Compose; o filesystem continua read-only. `docker compose down -v` apaga os dados (direito de eliminacao LGPD). No Azure, o Terraform monta um compartilhamento Azure Files em `/data`, com `nobrl` para o lock do SQLite funcionar sobre SMB, dono UID 10001 e `max_replicas = 1`, garantindo um unico escritor. A conta de armazenamento so aceita a sub-rede do Container Apps (firewall Deny, service endpoint), TLS 1.2 e criptografia de infraestrutura. Para escalar alem de 1 replica, migrar para banco gerenciado (por exemplo, PostgreSQL Flexible Server).

**Gate barrou a propria correcao.** A primeira versao do armazenamento persistente foi barrada pelo Trivy: CRITICAL AZU-0012, conta de armazenamento sem regras de rede. Corrigido com VNet dedicada e firewall Deny; o MEDIUM AZU-0061 foi corrigido com criptografia de infraestrutura. Riscos aceitos e documentados: AZU-0057 (logging de Queue; o projeto nao usa filas) e AZU-0058 (LRS em vez de GRS, para dados de demonstracao com retencao de 7 dias). Ambos estao abaixo do limiar HIGH/CRITICAL do gate.

**Deploy automatico.** O job `deploy` agora roda em todo push na `main` que passar em todos os gates, desde que `vars.DEPLOY_ENABLED == 'true'`; o disparo manual continua disponivel. Inclui health check pos-deploy contra a URL publica. Na `main` a concorrencia nao cancela um run em andamento, para nao interromper um deploy.

## Esteira barrada e corrigida no GitHub (2026-11-17)
Na branch `demo/pipeline-barrado`:
- Barrada: commit `6abd6ac` introduz `eval()` em `rpa/_gate_demo.py`. O passo "Semgrep local rules" falha com `devsecops.no-dynamic-evaluation` e o deploy é pulado: https://github.com/Acolhe-Projeto/Acolhe---GS8/actions/runs/44190586981
- Corrigida: commit `d68f2af` remove o arquivo e todos os gates passam: https://github.com/Acolhe-Projeto/Acolhe---GS8/actions/runs/44191227009

O workflow agora roda em push de qualquer branch, além de PR e disparo manual. O deploy continua restrito à `main`.

## Deploy automático configurado (OIDC, sem senha)
- Azure: identidade gerenciada `id-acolhe-gs8-deploy` em `rg-acolhe-gs8`. A credencial federada só aceita tokens do environment `production` com subject imutável `repo:Acolhe-Projeto@357388620/Acolhe---GS8@1451793339:environment:production`, e o papel Contributor fica limitado a esse resource group.
- GitHub: environment `production` restrito à branch `main`, sem aprovação manual (o controle humano fica no PR); secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` e `AZURE_SUBSCRIPTION_ID` no environment; variáveis `AZURE_RESOURCE_GROUP`, `AZURE_CONTAINER_APP` e `DEPLOY_ENABLED=true`.
- Registro privado (desde 18/11): a imagem testada vai para o Azure Container Registry `acracolhegs8hh2o2y` (Basic, sem usuário admin). A identidade de deploy tem `AcrPush`, e o app baixa a imagem com a identidade gerenciada `id-acolhe-gs8-pull` (`AcrPull`), sem senha nem pacote público. O job ficou sem `packages: write`: só pede `id-token` para o OIDC. Variável nova: `AZURE_ACR_NAME`.
- Deploy automático comprovado (18/11): o push `e3f6b6a` na `main` rodou build e todos os gates, enviou a imagem ao ACR (`sha256:f5a9dc44…`), atualizou o Container App e passou no health check da URL pública, sem nenhum passo manual: https://github.com/Acolhe-Projeto/Acolhe---GS8/actions/runs/44218099076. Os dados sobreviveram à nova revisão (2 sessões e 4 tentativas antes e depois).
- OIDC com subject imutável: a primeira tentativa desse run falhou no `azure/login` (`AADSTS700213`), porque o repositório usa subject imutável, `repo:Acolhe-Projeto@357388620/Acolhe---GS8@1451793339:environment:production`, com os IDs numéricos da organização e do repositório. A credencial federada foi trocada para esse formato, que também protege contra alguém recriar um repositório com o mesmo nome (o repositório já foi movido uma vez). A credencial antiga, por nome, foi removida.
- Por que mudou: o primeiro deploy pela `main` (run 44210859059) publicou no GHCR da organização, e o passo de verificação barrou o deploy porque o pacote era privado e só um owner da organização pode torná-lo público. O Azure não foi tocado. A troca para o ACR elimina a dependência de pacote público. Custo extra: US$ 0,1666/dia (cerca de US$ 5/mês). O Terraform deixa a tag da imagem com a CI (`ignore_changes`).

## Dashboard no Grafana apontando para o MVP publicado
```
docker compose -f devsecops/monitoring/public/compose.yaml up -d
```
O Prometheus (http://localhost:9091) coleta `/metrics` da URL pública por HTTPS, e o Grafana (http://localhost:3000) já sobe com o dashboard "Acolhe - Four Golden Signals" e o datasource provisionados. Verificado em 17/11 com 90 s de tráfego real na URL pública: up=1, latência média de 3,6 ms, cerca de 3 req/s, erros 0, saturação 0. O JSON do dashboard usava `${DS_PROMETHEUS}`, que só funciona em import manual, e passou a usar o uid fixo `prometheus`. Enquanto o Prometheus estiver coletando, o app não escala para zero: pare o stack depois dos prints (`docker compose ... down`).

## URL pública (Azure, 2026-11-14)
**https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io**

Criada pelo `terraform apply` deste diretório na assinatura Azure for Students, região `canadacentral`, porque a política da assinatura não permite `brazilsouth`. A persistência foi comprovada: os dados gravados pela API pública sobreviveram a dois reinícios do container, o segundo em réplica nova. Detalhes, os 3 defeitos encontrados no deploy real (pacote privado, provedor não registrado, subnet sem delegação) e as correções estão em `evidence/azure_deploy_20261114.md`.

Custos na região usada (Retail Prices API, canadacentral): vCPU US$ 0,000034/s, memória US$ 0,000004/GiB-s, US$ 0,40/milhão de requisições, Azure Files Hot LRS US$ 0,03/GB-mês. Incluindo ACR Basic (US$ 0,1666/dia, cerca de US$ 5/mês), uso de demonstração (40 h ativas/mês): ~US$ 6,70/mês; sempre ligado: ~US$ 33/mês. O crédito estudantil disponível é de US$ 100. As estimativas abaixo para brazilsouth são históricas e não representam o ambiente implantado.

O deploy automático da CI usa este mesmo Container App. OIDC, secrets e variáveis do environment `production` já foram configurados, incluindo `AZURE_ACR_NAME`, conforme a seção de deploy automático. A imagem fica no ACR privado; não é necessário tornar um pacote GHCR público.

## Docker real no WSL2 (2026-11-14, Ubuntu 26.04, Docker 29.1.3, Compose 2.40)
`bash devsecops/ci_local.sh` reproduz o job `test-and-build` da CI com as mesmas imagens e versoes (Gitleaks 8.24.2, Semgrep 1.111.0, Trivy 0.60.0). Resultado: ALL GATES PASSED, exit 0.
- Build da imagem; 73 testes dentro da imagem (1 ignorado, PyYAML opcional); smoke HTTP `/`, `/logo.png`, `/api/lessons`, `/api/summary`, `/api/gold`, `/metrics` = 200; UID 10001 grava SQLite em `/data`.
- Trivy 0.60.0 imagem: 0 HIGH/CRITICAL. Trivy 0.60.0 IaC: 0 HIGH/CRITICAL.
- Barrado e corrigido de novo: ao ampliar o escopo IaC para o repositorio inteiro, o Trivy 0.60.0 barrou HIGH DS-0017 em `devsecops/Dockerfile.candidate` (a 0.76.1 nao barrava). Esse arquivo e do experimento de imagem-base, nao e publicado, e o achado e falso positivo (`apt-get update` seguido de `upgrade` e limpeza do cache no mesmo RUN). O arquivo foi excluido com justificativa no workflow; Dockerfile de producao, Compose e Terraform continuam escaneados.

`bash devsecops/persistence_check.sh` (Compose com perfil monitoring): 0 sessoes -> 1 sessao/1 tentativa -> `docker compose down` + `up` com container novo -> continua 1/1. Rootfs somente leitura = true, usuario 10001, volume `acolhe-data`. O Prometheus no Docker coleta `app:8080`: `up{job="acolhe"} = 1`.

## Histórico de custos: brazilsouth (consulta de 2026-11-14, região não implantada)
vCPU ativa US$ 0,000024/s; memoria US$ 0,000003/GiB-s; requisicoes US$ 0,40/milhao. Container 0,25 vCPU e 0,5 GiB, escala 0..1.
- Demonstracao (40 h ativas/mes, 100 mil requisicoes): 36.000 vCPU-s = US$ 0,86; 72.000 GiB-s = US$ 0,22; requisicoes US$ 0,04. Total ~US$ 1,12/mes antes da franquia mensal gratuita do Container Apps, que nesta escala tende a zerar o valor (confirmar a franquia vigente na pagina de precos; a API nao a exibe).
- Pior caso, sempre ligado (730 h): 657.000 vCPU-s = US$ 15,77; 1.314.000 GiB-s = US$ 3,94; ~US$ 19,7/mes mais requisicoes.
- Azure Files (LRS, cota de 1 GiB) para o SQLite: centavos por mes; consultar o preco vigente da regiao antes do `apply`. VNet e service endpoint: sem custo.
- A estimativa original pressupunha GHCR público e não incluía ACR. O ambiente atual usa ACR Basic em canadacentral, com custo incluído na seção URL pública. O Terraform não cria Log Analytics. Para reproduzir a infraestrutura, revisar orçamento e preços da região antes do `apply`.

## Arquitetura
```
Dev -> PR -> GitHub Actions [testes Python/Node -> Gitleaks -> Semgrep -> build -> testes na imagem -> smoke HTTP/SQLite -> Trivy imagem -> Trivy IaC]
          \-> push main (gates verdes) -> ACR privado (imagem testada, push via OIDC) -> az containerapp update -> health check
Usuario -> HTTPS (ingress Azure) -> Container App acolhe (UID 10001, 0..1 replica) -> /data (Azure Files, firewall Deny)
Prometheus -> /metrics (latencia, trafego, erros, saturacao) -> regras de alerta (alerts.yml) -> Grafana (dashboard)
```
Componentes: app Python 3.12 da biblioteca padrao em imagem Alpine fixada por digest; SQLite com retencao de 7 dias; Terraform cria resource group, VNet/sub-rede, conta de armazenamento + share, ACR privado, identidade de pull, ambiente e Container App.

## Responsabilidade compartilhada
| Camada | Provedor (Azure/GitHub) | Equipe Acolhe |
|---|---|---|
| Datacenter, hardware, rede fisica, hipervisor | Azure | - |
| Plataforma Container Apps, patches do host, ingress TLS | Azure | escolher regiao, escala e ingress HTTPS-only |
| Runners do GitHub Actions | GitHub | fixar versoes das actions/ferramentas, nao expor segredos |
| Registro privado ACR | Azure | sem usuário admin, push pela CI e pull pela identidade gerenciada do app |
| Imagem do container (base, pacotes) | - | digest fixado, `apk upgrade`, Trivy bloqueando HIGH/CRITICAL, usuario nao root |
| Codigo da aplicacao | - | testes, Semgrep, validacao de entrada, CSP, protecao de origem |
| Identidade e acesso | Entra ID (OIDC) | identidade de deploy com menor privilegio, protecao de branch |
| Dados (SQLite, backups, retencao) | durabilidade do Azure Files (LRS) | classificacao, retencao de 7 dias, exclusao por sessao, firewall do storage |
| Monitoramento | coleta da plataforma | metricas de ouro, regras de alerta, resposta a incidente |

## LGPD
- Dados tratados: id de sessao aleatorio (pseudonimo), idioma, licao, acerto e horario. Nenhum nome, documento, foto, audio ou localizacao. A tela orienta usar adultos e dados de teste no piloto.
- Base legal e finalidade: uso academico demonstrativo. Em uso real com criancas, aplica-se o art. 14 (melhor interesse da crianca e consentimento especifico de um dos pais ou responsavel), alem de revisao do encarregado (DPO).
- Minimizacao e retencao: so o necessario ao exercicio, sessoes apagadas apos 7 dias (`app/core.py`) e botao "Apagar minha sessao de teste" (eliminacao a pedido). O RPA e o Big Data so exportam agregados, sem identificadores (testados).
- Seguranca (art. 46): TLS no ingress, container nao root e somente leitura, storage com firewall e criptografia, segredos fora do repositorio (Gitleaks), CSP e bloqueio de origem cruzada.
- Transferencia internacional (art. 33): a assinatura de estudante so permite regioes fora do Brasil, e o deploy esta em `canadacentral` (Canada). Ha transferencia internacional dos dados pseudonimos de sessao. Mitigacoes: dados minimos sem identificacao direta, retencao de 7 dias, criptografia em repouso e em transito, firewall do storage. Para uso real com criancas, usar `brazilsouth` numa assinatura que permita essa regiao, ou formalizar a base do art. 33 (por exemplo, clausulas-padrao contratuais). O ACR guarda apenas a imagem, sem dados pessoais.
- Pendente antes de uso real: autenticacao de educadores, protecao do `/metrics`, RIPD (relatorio de impacto), termo de consentimento e politica de privacidade revisados por juridico.

## Pipeline
`.github/workflows/devsecops.yml` executa testes da aplicação e robô, Gitleaks no histórico, Semgrep com regras locais, build, Trivy imagem e IaC. HIGH/CRITICAL bloqueiam; não há `continue-on-error`. Imagem testada é um artefato e o deploy utiliza esse mesmo tar. As tags de ferramentas estão fixadas em versões; endurecimento futuro: validar versões atuais e substituir tags por digests/SHA aprovados. Não alegar ausência de vulnerabilidades antes de rodar os scanners. Regras Semgrep locais são uma base pequena, não uma auditoria completa.

Deploy automático em push na `main` (nunca em PR), condicionado a `DEPLOY_ENABLED=true` e ao environment `production`; também pode ser disparado manualmente com `deploy=true`. O ambiente está configurado para a `main`, sem aprovação manual por deploy. O job autentica via OIDC, envia a imagem testada ao ACR privado e atualiza o Container App. Para reproduzir em outro ambiente, configurar secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` e variáveis `AZURE_ACR_NAME`, `AZURE_RESOURCE_GROUP`, `AZURE_CONTAINER_APP`, `DEPLOY_ENABLED`. O YAML sozinho não cria identidades, permissões ou regras de proteção de branch.

## IaC Azure aplicada
`terraform/main.tf` declara a infraestrutura usada no Azure: resource group, VNet/sub-rede, storage com firewall e share, ACR privado, identidade gerenciada de pull, Container Apps environment e Container App com HTTPS, escala 0..1 e robô simulado. O `apply` e a persistência estão registrados em `evidence/azure_deploy_20261114.md`; a configuração atual do ACR e o deploy automático estão documentados acima. Os custos atuais estão na seção URL pública e no PDF.

Para reproduzir: `terraform fmt -check`, `terraform init -backend=false`, `terraform validate`; depois gerar e revisar o plano antes de aplicar. Copiar `terraform.tfvars.example` localmente e substituir os valores; nunca versionar `.tfvars`, state ou plano com dados reais. `fmt`, `init` e `validate` foram executados, e a infraestrutura foi aplicada na assinatura de estudante. Para uso compartilhado, configurar backend remoto seguro com locking, restringir RBAC e manter o lockfile dos provedores.

## Observabilidade: quatro métricas
- Latência: `rate(acolhe_request_duration_seconds_sum[5m]) / clamp_min(rate(acolhe_request_duration_seconds_count[5m]), 0.001)`.
- Tráfego: `rate(acolhe_requests_total[5m])`.
- Erros: `rate(acolhe_errors_total[5m]) / clamp_min(rate(acolhe_requests_total[5m]), 0.001)`.
- Saturação: `acolhe_active_requests`, concorrência como proxy.

Prometheus coleta `/metrics` a cada 15s. Alertas incluem indisponibilidade por 2min e taxa de erros >5% por 5min, além de latência e concorrência. Configuração e regras foram verificadas com `promtool`, e o alerta de indisponibilidade foi observado em `firing` num ensaio local controlado. O dashboard Grafana foi provisionado e testado apontando para o MVP público. Alertas aparecem no Prometheus; Alertmanager e entrega externa não estão configurados, sem envio de mensagens.

## Evidências e limites da entrega
1. Build, testes, smoke HTTP/SQLite, UID 10001 e scanners: CI e execução Docker/WSL2 documentadas acima.
2. Esteira barrada e corrigida: runs de 17/11 com links na seção correspondente.
3. Terraform aplicado e persistência após reinícios: `evidence/azure_deploy_20261114.md`.
4. Deploy automático via OIDC e ACR: runs de 18/11, sem aprovação manual por deploy.
5. Dashboard dos quatro sinais e alerta disparado: prints no [PDF da entrega na main](https://github.com/Acolhe-Projeto/Acolhe---GS8/blob/main/docs/entregas/GS_DevSecOps_Acolhe.pdf).
6. Escopo acadêmico com dados de demonstração. As pendências antes de uso real estão na seção LGPD.

Repositório atual: https://github.com/Acolhe-Projeto/Acolhe---GS8/tree/main/devsecops .

### Quatro sinais de ouro
O dashboard `monitoring/grafana-dashboard.json` usa o datasource de uid `prometheus` e é provisionado pelo Compose de `monitoring/public/`. Foi testado no Grafana contra o MVP público, conforme a seção específica acima; também pode ser importado em uma instalação compatível.
- Latência: rate(acolhe_request_duration_seconds_sum[5m]) / rate(acolhe_request_duration_seconds_count[5m]), média, não p95.
- Tráfego: rate(acolhe_requests_total[5m]), requisições por segundo.
- Erros: rate(acolhe_errors_total[5m]) / clamp_min(rate(acolhe_requests_total[5m]), 0.001), proporção.
- Saturação: acolhe_active_requests, concorrência como proxy de saturação; não mede CPU/memória nem percentual de capacidade. Threshold inicial 20 requer calibração por teste de carga.
Há regras adicionais de latência média >1s e concorrência >20, ambas limiares provisórios. Métricas de tentativas/uptime complementam esses sinais, mas não os substituem.

O Docker usa ACOLHE_DB=/data/acolhe.db em volume gravavel do UID 10001 (Compose: volume `acolhe-data`), com o restante do filesystem read-only. Retencao de 7 dias aplicada pela aplicacao. As integrações genai/vision/rpa também são copiadas à imagem.


## Primeira CI pública e correção de imagem (2026-11-09)

O run https://github.com/TomazVC/Acolhe---GS8/actions/runs/42685134583, commit `624c6e77c003c88bba8edfc6a1b86f3f5403beed`, aprovou testes Python/Node, Gitleaks, Semgrep e build Docker. O Trivy bloqueou a imagem Debian 13.7: 49 ocorrências HIGH e nenhuma CRITICAL. São ocorrências por pacote, não necessariamente CVEs distintas.

Duas ocorrências em `zlib1g` tinham atualização indicada, para `1:1.3.dfsg+really1.3.1-1+deb13u1`. Outras estavam sem versão corrigida indicada ou com correção adiada pelo fornecedor. A imagem passa a aplicar as atualizações disponíveis da distribuição durante o build; a CI busca a imagem-base atual com `--pull`. Isso não garante ausência de vulnerabilidades sem correção. O bloqueio HIGH/CRITICAL continua ativo, sem `ignore-unfixed`, exceções de CVE ou supressão de erros. Consulte o run do commit atual antes de considerar a imagem aprovada. Nenhum deploy foi executado naquele ensaio de 09/11; os deploys posteriores estão registrados nas seções de Azure e OIDC.


### Alternativas oficiais avaliadas

O run https://github.com/TomazVC/Acolhe---GS8/actions/runs/42686110502 comparou imagens oficiais com atualização de pacotes, os 61 testes Python dentro de cada container (60 aprovados e 1 ignorado por PyYAML opcional), smoke HTTP e escrita/leitura SQLite com UID 10001, e Trivy com bloqueio HIGH/CRITICAL.

- `python:3.12-slim-bookworm`: testes aprovados, scan com 40 HIGH e 2 CRITICAL. Não adotada.
- `python:3.12-alpine`: testes e smoke aprovados; scan sem achados HIGH/CRITICAL na base Alpine 3.24.4. Adotada com o digest oficial verificado `sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7`, mantendo atualização de pacotes Alpine e todas as barreiras de segurança.

A CI principal agora também executa testes dentro da imagem e smoke HTTP/SQLite real antes do scan. A validação cobre o MVP de biblioteca padrão; não valida treinamento YOLO, dependências nativas opcionais, Airflow ou Databricks na imagem Alpine. Novas dependências precisam de nova verificação, pois Alpine usa musl em vez de glibc. O digest deve ser atualizado e revalidado periodicamente; um scan sem achados hoje não garante segurança futura. A branch `ci/evaluate-python-bases` preserva o experimento e não realiza deploy.
