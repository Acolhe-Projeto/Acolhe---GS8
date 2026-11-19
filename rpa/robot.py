from contextlib import closing
"""Read-only SQLite reporting robot. No email, external writes or identifiers."""
import argparse, json, logging, sqlite3, time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from app.core import LESSONS

KNOWN_LESSONS={lesson['id'] for lesson in LESSONS}

REVIEW_ACCURACY=0.6   # business rule: lessons below 60% accuracy need educator review
REVIEW_MIN_ATTEMPTS=3 # ...but only with enough attempts to be meaningful

def decide(attempts,lessons):
    """BPMN gateway 'Ha atividade? / Licao abaixo da meta?'. Returns status + lessons to review."""
    if attempts==0: return {'status':'sem_atividade','action':'Nenhuma atividade registrada; nada a consolidar.','lessons_to_review':[]}
    review=[l['lesson_id'] for l in lessons if l['attempts']>=REVIEW_MIN_ATTEMPTS and l['accuracy']<REVIEW_ACCURACY]
    if review: return {'status':'reforco_recomendado','action':'Revisar com educadores as licoes abaixo da meta de acerto.','lessons_to_review':review}
    return {'status':'progresso_adequado','action':'Sem intervencao necessaria.','lessons_to_review':[]}

def generate_report(database,output_dir):
    database=Path(database).resolve(); output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    logger=logging.getLogger('acolhe.rpa'); logger.setLevel(logging.INFO)
    handler=logging.FileHandler(output_dir/'robot.log',encoding='utf-8'); handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s')); logger.addHandler(handler)
    try:
        logger.info('report_started')
        if not database.is_file(): raise FileNotFoundError('Application database does not exist; start the MVP and complete an exercise first.')
        with closing(sqlite3.connect(database.as_uri()+'?mode=ro',uri=True,timeout=10)) as db:
            db.execute('PRAGMA query_only=ON')
            sessions=db.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
            # Older databases have only session language / no request_id; never rewrite their history.
            cols={row[1] for row in db.execute('PRAGMA table_info(attempts)')}
            language='COALESCE(a.language,s.language)' if 'language' in cols else 's.language'
            request='a.request_id' if 'request_id' in cols else 'a.id'
            by_lang={lang:[0,0] for (lang,) in db.execute('SELECT DISTINCT language FROM sessions')}
            rows=db.execute(f'SELECT a.session_id,a.lesson_id,a.correct,{request},{language},s.id FROM attempts a LEFT JOIN sessions s ON s.id=a.session_id').fetchall()
        # Batch loop with consistency rules: inconsistent rows are counted by reason, never aggregated.
        seen=set(); issues=Counter(); by_lesson={}; attempts=correct=0
        for session_id,lesson_id,ok,request_id,lang,session_exists in rows:
            if session_exists is None: issues['sessao_inexistente']+=1; continue
            if lesson_id not in KNOWN_LESSONS: issues['licao_desconhecida']+=1; continue
            if ok not in (0,1): issues['acerto_invalido']+=1; continue
            if (session_id,request_id) in seen: issues['tentativa_duplicada']+=1; continue
            seen.add((session_id,request_id)); attempts+=1; correct+=ok
            stats=by_lesson.setdefault(lesson_id,[0,0]); stats[0]+=1; stats[1]+=ok
            lang_stats=by_lang.setdefault(lang,[0,0]); lang_stats[0]+=1; lang_stats[1]+=ok
        if issues: logger.warning('inconsistent_rows skipped=%s reasons=%s',sum(issues.values()),json.dumps(dict(sorted(issues.items()))))
        languages=[{'language':l,'attempts':n,'correct':c} for l,(n,c) in sorted(by_lang.items(),key=lambda kv:str(kv[0]))]
        lessons=[{'lesson_id':lid,'attempts':n,'correct':c,'accuracy':round(c/n,4)} for lid,(n,c) in sorted(by_lesson.items())]
        decision=decide(attempts,lessons)
        logger.info('decision status=%s review=%s',decision['status'],','.join(decision['lessons_to_review']) or '-')
        report={'generated_at':datetime.now(timezone.utc).isoformat(),'scope':'local aggregate only; no personal identifiers','totals':{'sessions':sessions,'attempts':attempts,'correct':correct,'accuracy':round(correct/attempts,4) if attempts else 0},'by_language':languages,'by_lesson':lessons,'decision':decision,'data_quality':{'inconsistent_rows':sum(issues.values()),'by_reason':dict(sorted(issues.items()))}}
        temp=output_dir/'progress.tmp'; temp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); temp.replace(output_dir/'progress.json')
        review='\n'.join(f"- {l}" for l in decision['lessons_to_review']) or '- nenhuma'
        (output_dir/'progress.md').write_text(f"# Relatorio local Acolhe\n\nSessoes: {sessions}\nTentativas: {attempts}\nAcertos: {correct}\nTaxa de acerto: {report['totals']['accuracy']:.1%}\n\n## Decisao: {decision['status']}\n{decision['action']}\n\nLicoes para revisar:\n{review}\n\nDados agregados. Nao enviado a terceiros.\n",encoding='utf-8')
        logger.info('report_completed attempts=%s',attempts)
        return report
    except Exception as error:
        logger.error('report_failed type=%s',type(error).__name__)
        raise
    finally:
        logger.removeHandler(handler); handler.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--db',default='data/acolhe.db'); p.add_argument('--output',default='rpa/output')
    p.add_argument('--every',type=int,default=0,help='Built-in schedule: rerun every N seconds (0 = run once)')
    p.add_argument('--runs',type=int,default=0,help='With --every: stop after N runs (0 = until Ctrl+C)'); a=p.parse_args()
    if a.every<0 or a.runs<0: p.error('--every/--runs must be >= 0')
    done=failures=0
    try:
        while True:
            try: print(json.dumps(generate_report(a.db,a.output),ensure_ascii=False,indent=2),flush=True)
            except (OSError,sqlite3.Error) as error:
                failures+=1; print(f'RPA failed: {error}',flush=True)
                if not a.every: p.exit(1)
            done+=1
            if not a.every or (a.runs and done>=a.runs): break
            time.sleep(a.every)
    except KeyboardInterrupt: pass
    if failures: p.exit(1)
