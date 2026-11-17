# Databricks notebook source
# Databricks Runtime / serverless with Delta. Defaults target Free Edition (catalog "workspace").
# Run 00_setup_volume first; then run with batch_date=2026-11-05, 2026-11-06 and repeat to show idempotency.
# COMMAND ----------
from delta.tables import DeltaTable
from pyspark.sql import functions as F, Window
import re,json
from pathlib import Path
from datetime import date,datetime,timezone

dbutils.widgets.text('input_path','/Volumes/workspace/acolhe/data/input')
dbutils.widgets.text('output_path','/Volumes/workspace/acolhe/data/output')
dbutils.widgets.text('schema','workspace.acolhe')
dbutils.widgets.text('batch_date','2026-11-05')
input_path=dbutils.widgets.get('input_path').rstrip('/')
output_path=dbutils.widgets.get('output_path').rstrip('/')
namespace=dbutils.widgets.get('schema')
batch_date=dbutils.widgets.get('batch_date'); date.fromisoformat(batch_date)
assert re.fullmatch(r'[A-Za-z_]\w*\.[A-Za-z_]\w*',namespace),'Use catalog.schema identifiers'
spark.sql(f'CREATE SCHEMA IF NOT EXISTS {namespace}')
# COMMAND ----------
# COPY INTO tracks loaded file paths and skips them on subsequent executions.
# Input files are immutable; publish corrections under a NEW filename/date.
assert input_path.startswith('/Volumes/') and "'" not in input_path and "\\" not in input_path, 'Use a Unity Catalog volume path without quotes'
bronze=f'{namespace}.bronze'
spark.sql(f"""CREATE TABLE IF NOT EXISTS {bronze} (
 record_id STRING, region STRING, language STRING, count STRING,
 snapshot_date STRING, synthetic STRING, source STRING, batch_date STRING
) USING DELTA""")
for source in ('demand','services'):
    file_path=f'{input_path}/{source}_{batch_date}.csv'
    spark.sql(f"""COPY INTO {bronze}
    FROM (SELECT CAST(record_id AS STRING) AS record_id, CAST(region AS STRING) AS region,
                 CAST(language AS STRING) AS language, CAST(count AS STRING) AS count,
                 CAST(snapshot_date AS STRING) AS snapshot_date, CAST(synthetic AS STRING) AS synthetic,
                 '{source}' AS source, '{batch_date}' AS batch_date
          FROM '{file_path}')
    FILEFORMAT = CSV
    FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false', 'mode' = 'FAILFAST')
    COPY_OPTIONS ('force' = 'false')""")
# Bronze ingestion is COPY INTO, NOT MERGE. Silver retains business-key MERGE.
# COMMAND ----------
raw=spark.table(bronze)
raw=raw.withColumn('row_hash',F.sha2(F.to_json(F.struct(*[F.col(c) for c in raw.columns])),256))
clean=(raw.withColumn('record_id',F.trim('record_id')).withColumn('region',F.trim('region'))
    .withColumn('metric',F.expr('try_cast(count as BIGINT)'))
    .withColumn('day',F.expr('try_cast(snapshot_date as DATE)')))
# Quality rules (same codes as the local pipeline). A row is reported under the first rule it breaks.
r1=F.coalesce((F.length('record_id')>0)&(F.length('region')>0),F.lit(False))
r2=F.coalesce(F.col('language').isin('pt','es','en'),F.lit(False))
r3=F.coalesce((F.col('metric')>=0)&F.col('count').rlike('^[0-9]+$')&F.col('day').isNotNull()&F.col('synthetic').isin('true','false'),F.lit(False))
clean=clean.withColumn('rule_failed',F.when(~r1,'R1').when(~r2,'R2').when(~r3,'R3'))
valid=F.col('rule_failed').isNull()
clean.filter(~valid).write.format('delta').mode('overwrite').saveAsTable(f'{namespace}.quarantine')
RULES={'demand_services':[('R1','chave e territorio obrigatorios'),('R2','idioma permitido (pt/es/en)'),('R3','contagem inteira >= 0, data ISO e flag de origem')]}
def rule_counts(df,layer,rules):
    got={r['rule_failed']:r['n'] for r in df.filter(F.col('rule_failed').isNotNull()).groupBy('rule_failed').agg(F.count('*').alias('n')).collect()}
    return [(layer,code,desc,int(got.get(code,0))) for code,desc in rules]
quality_rows=rule_counts(clean,'demand_services',RULES['demand_services'])
window=Window.partitionBy('source','record_id').orderBy(F.col('day').desc(),F.col('batch_date').desc(),F.col('row_hash').desc())
latest=(clean.filter(valid).withColumn('rn',F.row_number().over(window)).filter('rn=1')
    .select('source','record_id','region','language',F.col('metric').alias('count'),F.col('day').alias('snapshot_date'),(F.col('synthetic')=='true').alias('synthetic')))
silver=f'{namespace}.silver'
if not spark.catalog.tableExists(silver): latest.limit(0).write.format('delta').saveAsTable(silver)
(DeltaTable.forName(spark,silver).alias('t').merge(latest.alias('s'),'t.source=s.source AND t.record_id=s.record_id')
 .whenMatchedUpdateAll(condition='s.snapshot_date >= t.snapshot_date').whenNotMatchedInsertAll().execute())
# COMMAND ----------
s=spark.table(silver)
regions=s.select('region').distinct().withColumn('region_id',F.sha2('region',256))
languages=s.select('language').distinct().withColumn('language_id',F.sha2('language',256))
regions.write.format('delta').mode('overwrite').saveAsTable(f'{namespace}.dim_region')
languages.write.format('delta').mode('overwrite').saveAsTable(f'{namespace}.dim_language')
fact=s.join(regions,'region').join(languages,'language').select('source','record_id','region_id','language_id','count','snapshot_date','synthetic')
fact.write.format('delta').mode('overwrite').saveAsTable(f'{namespace}.fact_indicators')
# COMMAND ----------
# Small aggregate exported for the MVP; detailed tables remain in Delta.
def grouped(column):
    rows=s.groupBy(column).pivot('source',['demand','services']).sum('count').fillna(0).orderBy(column).collect()
    return [r.asDict() for r in rows]
summary={'schema_version':1,'generated_at':datetime.now(timezone.utc).isoformat(),
 'synthetic':s.filter('synthetic=true').limit(1).count()>0,
 'source_batches':raw.select('source','batch_date').distinct().count(),
 'totals':{r['source']:r['total'] for r in s.groupBy('source').agg(F.sum('count').alias('total')).collect()},
 'by_region':grouped('region'),'by_language':grouped('language'),
 'quality':{'rejected':spark.table(f'{namespace}.quarantine').count(),'by_rule':{f'{c} {d}':n for _,c,d,n in quality_rows}},
 'provenance':{'mode':'Databricks normalized CSV import','sources':['demand','services']}}
# COMMAND ----------
# REAL batches from the Airflow landing zone (chegada/), uploaded to the Volume in batches
# by collection day (Databricks Free has no connection to Airflow). COPY INTO loads only
# files it has not seen; each row keeps its source file and load time.
chegada=f'{input_path}/chegada'
def _exists(p):
    try: dbutils.fs.ls(p); return True
    except Exception: return False
REAL={
 'municipios':{'folder':'ibge','pattern':'municipios_*.csv','key':['municipality_id'],
   'rules':[('M1','codigo IBGE com 7 digitos', F.col('municipality_id').rlike('^[0-9]{7}$')),
            ('M2','UF de SP (35/SP)', (F.col('state_id')=='35')&(F.col('state_code')=='SP')),
            ('M3','nome do municipio preenchido', F.length(F.trim('municipality'))>0)]},
 'obmigra':{'folder':'obmigra','pattern':'indicadores_*.csv','key':['indicator_id','reference_year','territory'],
   'rules':[('O1','indicador e territorio preenchidos', (F.length('indicator_id')>0)&F.col('territory').isin('BR','SP')),
            ('O2','valor numerico', F.expr("try_cast(value as DOUBLE)").isNotNull()),
            ('O3','pagina de origem valida', F.expr("try_cast(page as INT)").between(1,40))]}}
for name,cfg in REAL.items():
    folder=f"{chegada}/{cfg['folder']}"
    if not _exists(folder): print(f'{name}: sem lotes em {folder}'); continue
    assert "'" not in folder
    bronze_r=f'{namespace}.bronze_{name}'
    spark.sql(f'CREATE TABLE IF NOT EXISTS {bronze_r} USING DELTA')
    spark.sql(f"""COPY INTO {bronze_r}
      FROM (SELECT *, _metadata.file_name AS arquivo_origem, current_timestamp() AS carregado_em FROM '{folder}')
      FILEFORMAT = CSV PATTERN = '{cfg['pattern']}'
      FORMAT_OPTIONS ('header'='true','inferSchema'='false','mode'='FAILFAST')
      COPY_OPTIONS ('mergeSchema'='true','force'='false')""")
    b=spark.table(bronze_r)
    fail=None
    for code,_,ok in reversed(cfg['rules']): fail=F.when(~F.coalesce(ok,F.lit(False)),code).otherwise(fail if fail is not None else F.lit(None))
    b=b.withColumn('rule_failed',fail)
    quality_rows+=rule_counts(b,name,[(c,d) for c,d,_ in cfg['rules']])
    w=Window.partitionBy(*cfg['key']).orderBy(F.col('collected_on').desc(),F.col('arquivo_origem').desc())
    latest=b.filter(F.col('rule_failed').isNull()).withColumn('rn',F.row_number().over(w)).filter('rn=1').drop('rn','rule_failed','carregado_em')
    silver_r=f'{namespace}.silver_{name}'
    if not spark.catalog.tableExists(silver_r): latest.limit(0).write.format('delta').saveAsTable(silver_r)
    cond=' AND '.join(f't.{k}=s.{k}' for k in cfg['key'])
    (DeltaTable.forName(spark,silver_r).alias('t').merge(latest.alias('s'),cond)
       .whenMatchedUpdateAll(condition='s.collected_on >= t.collected_on').whenNotMatchedInsertAll().execute())
# Gold from the real Silver tables (IDs only for municipalities; no personal data exists here).
if spark.catalog.tableExists(f'{namespace}.silver_municipios'):
    (spark.table(f'{namespace}.silver_municipios').select(F.col('municipality_id').cast('int').alias('municipality_id'),'municipality','state_code','state','collected_on')
       .write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable(f'{namespace}.dim_municipality'))
if spark.catalog.tableExists(f'{namespace}.silver_obmigra'):
    (spark.table(f'{namespace}.silver_obmigra').select('indicator_id',F.col('reference_year').cast('int').alias('reference_year'),'territory',
        F.col('value').cast('double').alias('value'),'unit','label_pt',F.col('page').cast('int').alias('page'),'collected_on')
       .write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable(f'{namespace}.gold_official_context'))
    oc=spark.table(f'{namespace}.gold_official_context').collect()
    summary['official_context']={'synthetic':False,'reference_year':2025,'indicators':[r.asDict() for r in oc],
        'note':'Indicadores oficiais de contexto; nao somados a camada sintetica.'}
spark.createDataFrame(quality_rows,'layer string, rule string, description string, barrados long').withColumn('medido_em',F.current_timestamp()) \
    .write.format('delta').mode('overwrite').saveAsTable(f'{namespace}.quality_rules')
display(spark.table(f'{namespace}.quality_rules'))
Path(output_path).mkdir(parents=True,exist_ok=True)
Path(output_path,'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
display(fact)
print(json.dumps(summary,ensure_ascii=False,indent=2))
