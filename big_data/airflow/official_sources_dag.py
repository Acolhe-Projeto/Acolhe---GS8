"""Airflow 3: daily collection of the real sources into chegada/ (landing zone).

coletar_ibge and coletar_obmigra run in parallel, each writing one file per collection
with the date in the name; conferir_chegada then checks both files arrived. Failures and
the successful check are sent to the notification channel (chegada/_notificacoes).
Endpoints come from Airflow Variables (acolhe_ibge_url, acolhe_obmigra_url); the sources
are public and need no key, and no secret is ever written in this file.
"""
import os, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from airflow.sdk import Variable, dag, task

def _root():
    root = Path(os.environ['ACOLHE_ROOT'])
    if str(root) not in sys.path: sys.path.insert(0, str(root))
    return root

def _paths():
    root = _root()
    return root / 'big_data' / 'chegada', root / 'big_data' / 'official_snapshots'

def notificar_falha(context):
    from big_data.chegada import notify
    ti = context.get('ti')
    notify(_paths()[0], 'task_failure', dag_id=getattr(ti, 'dag_id', None), task_id=getattr(ti, 'task_id', None),
           try_number=getattr(ti, 'try_number', None), error=type(context.get('exception')).__name__)

@dag(dag_id='acolhe_official_snapshots', schedule='0 4 * * *', start_date=datetime(2026, 11, 7, tzinfo=timezone.utc),
     catchup=False, max_active_runs=1, tags=['acolhe', 'official', 'chegada'],
     default_args={'retries': 2, 'retry_delay': timedelta(minutes=3), 'on_failure_callback': notificar_falha})
def official_snapshots():
    @task
    def coletar_ibge():
        from big_data.chegada import land_ibge
        chegada, snapshots = _paths()
        return land_ibge(chegada, snapshots, url=Variable.get('acolhe_ibge_url', default=None))

    @task
    def coletar_obmigra():
        from big_data.chegada import land_obmigra
        chegada, snapshots = _paths()
        return land_obmigra(chegada, snapshots, url=Variable.get('acolhe_obmigra_url', default=None))

    @task
    def conferir_chegada(ibge, obmigra):
        from big_data.chegada import check_arrival, notify
        chegada, _ = _paths()
        result = check_arrival(chegada)
        notify(chegada, 'chegada_ok', **result, new_files=[r['file'] for r in (ibge, obmigra) if r['new_file']])
        return result

    conferir_chegada(coletar_ibge(), coletar_obmigra())

official_sources_dag = official_snapshots()
