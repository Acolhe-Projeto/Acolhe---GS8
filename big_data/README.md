# Big Data: Acolhe

## Integrantes
- Tomáz Versolato Carballo, RM 551417
- Rony Ken Nagai, RM 551549
- Aksel Viktor Caminha Rae, RM 99011
- Ian Xavier Kuraoka, RM 98860

## Requisitos 01 a 09 da GS
| # | Requisito | Onde está |
|---|---|---|
| 01 | Duas fontes, uma externa real | IBGE (API de Localidades) e OBMigra 2025 (relatório oficial), além das fontes demonstrativas `demand`/`services`. Licenças em `OFFICIAL_SOURCES.md`. |
| 02 | DAG agendado grava em `chegada/`, um arquivo por coleta com data | `airflow/official_sources_dag.py` (diário, 04:00 UTC) grava `chegada/ibge/municipios_AAAA-MM-DD.csv` e `chegada/obmigra/indicadores_AAAA-MM-DD.csv`. A data é o dia real da coleta (UTC), e um arquivo existente nunca é sobrescrito. |
| 03 | Paralelismo, conferência e chaves fora do código | `coletar_ibge` e `coletar_obmigra` em paralelo, seguidas de `conferir_chegada` (arquivo existe, tem cabeçalho e não está vazio). Falhas acionam `on_failure_callback` e a conferência registra `chegada_ok` em `chegada/_notificacoes/notificacoes.jsonl`. Os endpoints vêm das Variables `acolhe_ibge_url` e `acolhe_obmigra_url`; as fontes são públicas e não usam chave. |
| 04 | Dois lotes de dias diferentes no Volume | Lotes reais de 14/11 e 17/11 enviados ao Volume em `input/chegada/` (`databricks/run_evidence.py`, por dia de coleta). |
| 05 | Bronze incremental sem duplicar | `COPY INTO` com `force=false` em `bronze` (demo), `bronze_municipios` e `bronze_obmigra`, com `arquivo_origem` e `carregado_em` em cada linha. Execução limpa em `evidence/databricks_20261117_acolhe_gs.md`: bronze_municipios 0 → 645 (lote de 14/11) → 1290 (lote de 17/11) → 1290 (reexecução); prata 645. |
| 06 | Prata com tipos, nulos, MERGE e 3 regras com contagem | Regras R1/R2/R3 (demo), M1/M2/M3 (municípios) e O1/O2/O3 (OBMigra); o total barrado por regra fica na tabela `quality_rules`. O lote `demand_2026-11-07.csv` é um lote sintético de teste, com uma linha inválida por regra. |
| 07 | Ouro com fato, 2 dimensões e 5 consultas, uma de impacto | `fact_indicators`, `dim_region`, `dim_language`, `dim_municipality` e `gold_official_context`; 8 consultas em `queries.sql`, interpretadas em `EVIDENCIAS.md`. A consulta 6 (crianças solicitantes de refúgio) é a de impacto. |
| 08 | LGPD na Ouro e tela do MVP | Não há dado pessoal em nenhuma camada, e as chaves das dimensões no Databricks são hash SHA-256. O MVP consome `summary.json` em `/api/gold` (painel "Território e acolhimento"). |
| 09 | README com integrantes, arquitetura e passo a passo | Este arquivo. Amostras de cada fonte em `amostras/`. |


## Estado e honestidade dos dados
Executado localmente em Python 3.12 + SQLite. Os indicadores de demanda/servicos do MVP sao inteiramente SINTETICOS: nao representam refugiados reais, demanda real nem capacidade de atendimento. Duas fontes logicas de demonstracao (`demand` e `services`), nao duas bases publicas ja integradas. Referencias oficiais adicionais foram adquiridas separadamente em official_snapshots; veja OFFICIAL_SOURCES.md. Nao houve execucao Airflow ou Databricks, nem criacao de conta/cluster. Isso permanece pendente para evidencia academica.

## Fontes reais integradas (2026-11-14)
Tres fontes: `demand`/`services` (demonstrativas, synthetic=true) e duas externas reais, OBMigra/MJSP 2025 e IBGE Localidades.
```
python -B -m big_data.collect_official --source all      # coleta real (manifesto com dia UTC)
python -B -m big_data.pipeline                           # medalhao demonstrativo
python -B -m big_data.official_integration               # integra OBMigra + IBGE
```
`official_integration.py` le o snapshot mais recente, confere o SHA-256 do manifesto e extrai 7 indicadores do texto do PDF (as tabelas e graficos do relatorio sao imagens, sem texto extraivel). Cada indicador tem pagina, trecho de evidencia e regex ancorada: se o texto mudar, a extracao falha, sem chute nem OCR. Valores obtidos: 75.600 pedidos de refugio em 2025 (+10,9%), 16,0% criancas de 0 a 11 anos, 9.200 deferidos (24,4% criancas), 199.600 regularizados, Sao Paulo/SP -2,5%. O IBGE vira `dim_municipality` (645 municipios de SP).
Tabelas: `official_batches` (lotes por hash e dia), `silver_official_indicator` (UPSERT), `dim_municipality`, `gold_official_context`. O `summary.json` ganha `official_context` com synthetic=false; o selo synthetic=true do topo continua valendo para demanda/servicos, e os numeros oficiais nunca sao somados a eles. Consultas 6 a 8 de `queries.sql` usam essas tabelas. Uma reexecucao mantem as contagens (7 / 645 / 2).
Base de reuso: a p.4 do relatorio permite reproduzir texto e dados citando a fonte, sem fins comerciais. O PDF bruto continua fora do Git.
Segundo dia real: coleta feita em 2026-11-14 UTC (IBGE HTTP 200, 645 municipios, sha256 c06b7327...; OBMigra HTTP 200, 11.428.175 bytes, sha256 36bf2281...). Os manifestos de 2026-11-07 ficaram na maquina da primeira coleta: copie-os para `official_snapshots/manifests` para que `retrieval_days_utc` mostre os dois dias.

## Airflow: execucao real (2026-11-14, WSL2 + Docker)
```
docker compose -f big_data/airflow/compose.airflow.yaml up -d     # UI: http://localhost:8081
bash big_data/airflow/run_evidence.sh 2                            # dispara os DAGs e imprime estados e contagens
```
Imagem oficial `apache/airflow:3.1.0-python3.12` em modo standalone, montando o repositorio e lendo os DAGs de `big_data/airflow`. Log completo em `evidence/airflow_run_20261114.txt`.
- `acolhe_medallion`, execucao 1 e execucao 2: dag run = success. `ingest_demand` e `ingest_services` comecaram com 1 ms de diferenca (paralelas), depois `medallion` e `integrate_official`, todas success.
- Contagens identicas nas duas execucoes: lotes=4, bronze=8, prata=4, quarentena=0, fato=4, lotes oficiais=2, indicadores=7, municipios=645, logo nao houve duplicidade. O warehouse ja tinha os lotes antes da execucao 1; as contagens lote a lote estao em `EVIDENCIAS.md`.
- `acolhe_official_snapshots`: `collect_ibge_territory` e `collect_obmigra_report` em paralelo, depois `summarize`, todas success (coleta real pela internet).
- A primeira execucao real revelou dois defeitos, ja corrigidos: EPERM no `shutil.copy2` (o worker roda como UID 50000) e PyMuPDF ausente na imagem (`requirements-official.txt`). Detalhes em VERIFICATION.md.
- `test_airflow_dag.py` continua cobrindo a logica das tarefas na CI, sem scheduler.
- Para o PDF, capture o grafo e a aba de logs em http://localhost:8081 (acesso local, sem login).

## Rodar e testar
Na raiz acolhe:
```
python -B -m big_data.pipeline --demo
python -B -m unittest big_data.test_pipeline -v
```
O primeiro comando gera 4 CSVs: 2 fontes x datas 2026-11-05 e 2026-11-06. Sao datas dos dados, NAO comprovacao de execucoes em dois dias. A segunda data atualiza as mesmas chaves. Repetir nao duplica bronze nem prata. Resultado esperado: bronze=8, prata=4; demanda=190, servicos=40. `output/warehouse.db` e CSVs exportados permitem auditoria; `output/summary.json` e o contrato consumido pelo MVP.

## Arquitetura
CSV -> bronze imutavel por hash do arquivo + numero da linha -> prata UPSERT por (source,record_id) priorizando snapshot mais recente -> ouro fato + dimensoes territorio e idioma -> JSON da aplicacao.
Bronze preserva payload bruto. Arquivos novos sao incrementais; arquivos identicos sao ignorados. Correcoes no mesmo dia substituem prata na ordem lexicografica dos arquivos; produtores devem evitar conflitos de chave/data ou publicar snapshot de data mais recente. A quarentena registra rejeicoes por lote/linha. Nao ha exclusao logica automatica: ausencia em lote nao remove registros anteriores.

Regras de qualidade: (1) chave e territorio obrigatorios; (2) idioma pt/es/en; (3) contagem inteira nao negativa, data ISO e marcacao de origem explicita. Registros invalidos permanecem bronze e entram quarentena. Os testes cobrem lote repetido, atualizacao, ouro e rejeicao. As cinco consultas em queries.sql usam as tabelas ouro. Grao do fato: indicador mais recente por fonte/chave; nao e uma serie historica. Bronze preserva o historico.

## Contrato de integracao
Schema v1: generated_at UTC, synthetic boolean (verdadeiro se qualquer registro for sintetico), source_batches inteiro, totals {demand,services}, by_region [{region,demand,services}], by_language [{language,demand,services}], quality.rejected, provenance. A tela deve manter selo de dados demonstrativos quando synthetic=true. Os indicadores nao decidem elegibilidade individual e nao devem ser apresentados como estatisticas oficiais.

## Adaptador de fontes reais
A interface de ingestao real e CSV normalizado, sem requisicoes de rede ou credenciais. Exporte dados permitidos, documente licenca, data e transformacoes, e grave `demand_YYYY-MM-DD.csv` e `services_YYYY-MM-DD.csv` em uma pasta nova. Cabecalho obrigatorio:
```
record_id,region,language,count,snapshot_date,synthetic
```
Use synthetic=false SOMENTE quando a linha vier de fonte real verificada. Rode `python -m big_data.pipeline --input caminho --output big_data/output_real`. Nao misture a base demonstrativa com a real. Os arquivos reais devem conter apenas agregados, nunca nomes, documentos ou identificadores de pessoas. O adaptador normalizado nao faz correspondencia automatica entre conceitos/idiomas de bases oficiais.

Possiveis fontes para pesquisa futura: portal de dados UNHCR (https://www.unhcr.org/refugee-statistics/) e CadSUAS/MDS (https://aplicacoes.mds.gov.br/cadsuas/). Disponibilidade, granularidade, permissao e mapeamento ainda precisam de validacao; nao sao afirmadas como fontes dos CSVs entregues.

## Airflow
`airflow/acolhe_dag.py`: alvo Airflow 3 (`from airflow.sdk import dag, task`), nao instalado/executado nesta entrega. Instale em Linux/WSL/container seguindo as instrucoes oficiais. Monte o repositorio em todos os workers, configure ACOLHE_ROOT e opcional ACOLHE_IMPORT_DIR; coloque o DAG no dags_folder. Duas tarefas irmas ingest_demand e ingest_services copiam/validam arquivos em paralelo; medallion depende das duas. Requer executor com pelo menos 2 slots; max_active_runs=1 evita corrida SQLite. Agenda diaria 03:00 UTC, retries=2. O DAG executa o pipeline LOCAL, nao envia jobs Databricks. A integracao com Databricks Jobs e uma etapa pendente, e nao deve ser inferida pelo desenho.

## Databricks
Importe databricks/medallion.py como notebook; configure catalog.schema e paths de um Unity Catalog Volume existente ao qual tenha acesso. Carregue os 4 CSVs no volume (upload requer sua autorizacao). Execute batch_date=2026-11-05 e depois 2026-11-06; repita a segunda execucao e confira contagens. Para a exigencia de dias de execucao diferentes, agende e execute em dois dias reais e capture logs/timestamps, nao apenas dois valores de widget. O notebook implementa bronze incremental com COPY INTO (force=false), prata MERGE com deduplicacao, quarentena e ouro Delta. Copie o summary.json do volume para output somente depois de conferir origem e schema. Nao ha credenciais em codigo.

## Evidencias pendentes
- Selecionar/adquirir duas fontes reais compativeis se exigidas pelo professor.
- Executar DAG, registrar grafico com branches paralelos e logs.
- Executar notebook em Databricks em dois dias distintos e guardar historico Delta (`DESCRIBE HISTORY`) e contagens antes/depois/reexecucao.
- Executar e capturar as cinco consultas ouro no workspace.
- Validar custeio e permissao do ambiente antes de provisionar infraestrutura.

Referencias tecnicas consultadas em 2026-11-07: https://docs.databricks.com/aws/en/delta/merge ; https://docs.databricks.com/aws/en/delta/tutorial ; https://airflow.apache.org/docs/task-sdk/stable/ ; https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/examples .

## Atualizacao dos requisitos (PDF p.34-35)
Airflow foi ajustado para API publica 3.x. Databricks usa COPY INTO na bronze; o MERGE continua somente na prata. COPY INTO lembra arquivos ja ingeridos: nao altere um arquivo apos ingestao, publique correcao sob novo caminho/data. Nao use force=true para demonstrar idempotencia. O notebook requer schema vazio/compatível; se executou uma versao anterior com esquema diferente, use outro schema e preserve a evidencia antiga. As verificacoes locais de configuracao sao estaticas, nao equivalem a execucao Airflow/Spark.

Um segundo DAG, airflow/official_sources_dag.py, prepara aquisicoes IBGE e OBMigra em tarefas paralelas e so resume proveniencia. Nao fabrica uma uniao semantica dessas referencias com demanda/oferta e nao foi ativado. A agenda descrita no arquivo nao esta instalada em nenhum scheduler.
