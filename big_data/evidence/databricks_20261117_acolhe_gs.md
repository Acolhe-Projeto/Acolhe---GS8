# Evidencias Databricks (2026-11-17 23:16 UTC)

Workspace Databricks Free Edition (serverless). Git folder da branch `Aksel+Ian`, commit `9dbee0b`. Gerado por `big_data/databricks/run_evidence.py`.

## Execucoes

| Notebook | Parametros | Inicio (UTC) | Resultado | Run |
|---|---|---|---|---|
| acolhe-00_setup_volume-setup | {"catalog": "workspace", "schema": "acolhe_gs"} | 2026-11-17T23:09:16+00:00 | SUCCESS | https://dbc-f8b0fc62-f5ec.cloud.databricks.com/?o=7474655582396358#job/141500460656912/run/4773285045186 |
| acolhe-medallion-2026-11-05 | {"batch_date": "2026-11-05", "schema": "workspace.acolhe_gs", "input_path": "/Volumes/workspace/acolhe_gs/data/input", "output_path": "/Volumes/workspace/acolhe_gs/data/output"} | 2026-11-17T23:09:52+00:00 | SUCCESS | https://dbc-f8b0fc62-f5ec.cloud.databricks.com/?o=7474655582396358#job/264213843131650/run/394112056447984 |
| acolhe-medallion-2026-11-06 | {"batch_date": "2026-11-06", "schema": "workspace.acolhe_gs", "input_path": "/Volumes/workspace/acolhe_gs/data/input", "output_path": "/Volumes/workspace/acolhe_gs/data/output"} | 2026-11-17T23:11:21+00:00 | SUCCESS | https://dbc-f8b0fc62-f5ec.cloud.databricks.com/?o=7474655582396358#job/233520774485549/run/683882038892704 |
| acolhe-medallion-2026-11-07 | {"batch_date": "2026-11-07", "schema": "workspace.acolhe_gs", "input_path": "/Volumes/workspace/acolhe_gs/data/input", "output_path": "/Volumes/workspace/acolhe_gs/data/output"} | 2026-11-17T23:13:17+00:00 | SUCCESS | https://dbc-f8b0fc62-f5ec.cloud.databricks.com/?o=7474655582396358#job/297722192812842/run/398210219699031 |
| acolhe-medallion-2026-11-07 | {"batch_date": "2026-11-07", "schema": "workspace.acolhe_gs", "input_path": "/Volumes/workspace/acolhe_gs/data/input", "output_path": "/Volumes/workspace/acolhe_gs/data/output"} | 2026-11-17T23:14:49+00:00 | SUCCESS | https://dbc-f8b0fc62-f5ec.cloud.databricks.com/?o=7474655582396358#job/121712913603676/run/821220335308384 |

## Lotes reais enviados ao Volume

| Dia de coleta | Arquivos |
|---|---|
| 2026-11-14 | ibge/municipios_2026-11-14.csv, obmigra/indicadores_2026-11-14.csv |
| 2026-11-17 | ibge/municipios_2026-11-17.csv, obmigra/indicadores_2026-11-17.csv |

## Contagens antes, depois de cada lote e na reexecucao

| Etapa | bronze | silver | quarantine | fact_indicators | bronze_municipios | silver_municipios | bronze_obmigra | silver_obmigra | dim_municipality | gold_official_context |
|---|---|---|---|---|---|---|---|---|---|---|
| Antes | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Depois do lote demo 05/11 | 4 | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| Depois do lote real 2026-11-14 (+ demo 06/11) | 8 | 4 | 0 | 4 | 645 | 645 | 7 | 7 | 645 | 7 |
| Depois do lote real 2026-11-17 (+ demo 07/11, teste de qualidade) | 11 | 4 | 3 | 4 | 1290 | 645 | 14 | 7 | 645 | 7 |
| Reexecucao (nenhum arquivo novo) | 11 | 4 | 3 | 4 | 1290 | 645 | 14 | 7 | 645 | 7 |

## Bronze real por arquivo de origem

| arquivo_origem | collected_on | linhas |
|---|---|---|
| municipios_2026-11-14.csv | 2026-11-14 | 645 |
| municipios_2026-11-17.csv | 2026-11-17 | 645 |

## Regras de qualidade da Prata (total barrado por regra)

| layer | rule | description | barrados |
|---|---|---|---|
| demand_services | R1 | chave e territorio obrigatorios | 1 |
| demand_services | R2 | idioma permitido (pt/es/en) | 1 |
| demand_services | R3 | contagem inteira >= 0, data ISO e flag de origem | 1 |
| municipios | M1 | codigo IBGE com 7 digitos | 0 |
| municipios | M2 | UF de SP (35/SP) | 0 |
| municipios | M3 | nome do municipio preenchido | 0 |
| obmigra | O1 | indicador e territorio preenchidos | 0 |
| obmigra | O2 | valor numerico | 0 |
| obmigra | O3 | pagina de origem valida | 0 |

## DESCRIBE HISTORY bronze

| version | timestamp | operation | operationMetrics |
|---|---|---|---|
| 5 | 2026-11-17T23:13:33.000Z | COPY INTO | {"numFiles":"1","numOutputRows":"3","numOutputBytes":"2604","numSkippedCorruptFiles":"0"} |
| 4 | 2026-11-17T23:11:45.000Z | COPY INTO | {"numFiles":"1","numOutputRows":"2","numOutputBytes":"2516","numSkippedCorruptFiles":"0"} |
| 3 | 2026-11-17T23:11:42.000Z | COPY INTO | {"numFiles":"1","numOutputRows":"2","numOutputBytes":"2507","numSkippedCorruptFiles":"0"} |
| 2 | 2026-11-17T23:10:15.000Z | COPY INTO | {"numFiles":"1","numOutputRows":"2","numOutputBytes":"2512","numSkippedCorruptFiles":"0"} |
| 1 | 2026-11-17T23:10:12.000Z | COPY INTO | {"numFiles":"1","numOutputRows":"2","numOutputBytes":"2508","numSkippedCorruptFiles":"0"} |
| 0 | 2026-11-17T23:10:08.000Z | CREATE TABLE | {} |

## DESCRIBE HISTORY bronze_municipios

| version | timestamp | operation | operationMetrics |
|---|---|---|---|
| 2 | 2026-11-17T23:13:55.000Z | COPY INTO | {"numFiles":"1","numOutputRows":"645","numOutputBytes":"8660","numSkippedCorruptFiles":"0"} |
| 1 | 2026-11-17T23:12:06.000Z | COPY INTO | {"numFiles":"1","numOutputRows":"645","numOutputBytes":"8660","numSkippedCorruptFiles":"0"} |
| 0 | 2026-11-17T23:12:04.000Z | CREATE TABLE | {} |

## DESCRIBE HISTORY silver

| version | timestamp | operation | operationMetrics |
|---|---|---|---|
| 4 | 2026-11-17T23:15:11.000Z | MERGE | {"numTargetRowsCopied":"0","numTargetRowsDeleted":"0","numTargetFilesAdded":"1","numTargetBytesAdded":"2995","numTargetBytesRemoved":"2995","numTargetDeletionVe |
| 3 | 2026-11-17T23:13:40.000Z | MERGE | {"numTargetRowsCopied":"0","numTargetRowsDeleted":"0","numTargetFilesAdded":"1","numTargetBytesAdded":"2995","numTargetBytesRemoved":"2994","numTargetDeletionVe |
| 2 | 2026-11-17T23:11:51.000Z | MERGE | {"numTargetRowsCopied":"0","numTargetRowsDeleted":"0","numTargetFilesAdded":"1","numTargetBytesAdded":"2994","numTargetBytesRemoved":"2255","numTargetDeletionVe |
| 1 | 2026-11-17T23:10:25.000Z | MERGE | {"numTargetRowsCopied":"0","numTargetRowsDeleted":"0","numTargetFilesAdded":"1","numTargetBytesAdded":"2255","numTargetBytesRemoved":"0","numTargetDeletionVecto |
| 0 | 2026-11-17T23:10:22.000Z | CREATE TABLE AS SELECT | {"numFiles":"0","numOutputRows":"0","numOutputBytes":"0"} |

## Consultas ouro no Databricks

### Consulta 1

```sql
SELECT r.region, SUM(f.count) AS demand FROM workspace.acolhe_gs.fact_indicators f JOIN workspace.acolhe_gs.dim_region r USING(region_id) WHERE source='demand' GROUP BY r.region ORDER BY demand DESC
```

| region | demand |
|---|---|
| Sao Paulo | 110 |
| Parana | 80 |

### Consulta 2

```sql
SELECT r.region, SUM(f.count) AS services FROM workspace.acolhe_gs.fact_indicators f JOIN workspace.acolhe_gs.dim_region r USING(region_id) WHERE source='services' GROUP BY r.region ORDER BY services DESC
```

| region | services |
|---|---|
| Sao Paulo | 22 |
| Parana | 18 |

### Consulta 3

```sql
SELECT l.language,SUM(f.count) AS demand FROM workspace.acolhe_gs.fact_indicators f JOIN workspace.acolhe_gs.dim_language l USING(language_id) WHERE source='demand' GROUP BY l.language
```

| language | demand |
|---|---|
| pt | 80 |
| es | 110 |

### Consulta 4

```sql
SELECT r.region, SUM(CASE WHEN source='demand' THEN count ELSE 0 END)*1.0/NULLIF(SUM(CASE WHEN source='services' THEN count ELSE 0 END),0) AS demand_per_service FROM workspace.acolhe_gs.fact_indicators f JOIN workspace.acolhe_gs.dim_region r USING(region_id) GROUP BY r.region
```

| region | demand_per_service |
|---|---|
| Sao Paulo | 5.0000000000000000 |
| Parana | 4.4444444444444444 |

### Consulta 5

```sql
SELECT source,MIN(snapshot_date) AS oldest_snapshot,MAX(snapshot_date) AS newest_snapshot,SUM(CASE WHEN synthetic THEN 1 ELSE 0 END) AS synthetic_records,COUNT(*) AS records FROM workspace.acolhe_gs.fact_indicators GROUP BY source
```

| source | oldest_snapshot | newest_snapshot | synthetic_records | records |
|---|---|---|---|---|
| demand | 2026-11-06 | 2026-11-06 | 2 | 2 |
| services | 2026-11-06 | 2026-11-06 | 2 | 2 |

### Consulta 6

```sql
SELECT t.value AS refugee_requests, c.value AS children_pct, ROUND(t.value*c.value/100.0) AS estimated_children_requests FROM workspace.acolhe_gs.gold_official_context t JOIN workspace.acolhe_gs.gold_official_context c ON c.indicator_id='refugee_requests_children_0_11_pct' WHERE t.indicator_id='refugee_requests_total'
```

| refugee_requests | children_pct | estimated_children_requests |
|---|---|---|
| 75600.0 | 16.0 | 12096.0 |

### Consulta 7

```sql
SELECT ROUND(r.value*100.0/q.value,1) AS recognized_per_100_requests FROM workspace.acolhe_gs.gold_official_context r JOIN workspace.acolhe_gs.gold_official_context q ON q.indicator_id='refugee_requests_total' WHERE r.indicator_id='refugee_recognized_total'
```

| recognized_per_100_requests |
|---|
| 12.2 |

### Consulta 8

```sql
SELECT (SELECT COUNT(*) FROM workspace.acolhe_gs.dim_municipality WHERE state_code='SP') AS ibge_sp_municipalities, (SELECT COUNT(*) FROM workspace.acolhe_gs.dim_region) AS demo_regions
```

| ibge_sp_municipalities | demo_regions |
|---|---|
| 645 | 2 |
