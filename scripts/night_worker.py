"""Bounded, restartable local experiments. Never promotes, publishes or uses test23."""
import contextlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STATE = ROOT/'docs/qa/night'
JOBS = [
    {'name': '26-freeze10-640', 'base_model': 'yolo26n.pt', 'epochs': 120, 'imgsz': 640, 'batch': 2, 'freeze': 10},
    {'name': '26-freeze22-640', 'base_model': 'yolo26n.pt', 'epochs': 120, 'imgsz': 640, 'batch': 2, 'freeze': 22},
    {'name': '26-freeze10-960', 'base_model': 'yolo26n.pt', 'epochs': 100, 'imgsz': 960, 'batch': 1, 'freeze': 10},
    {'name': 'v8-freeze10-640', 'base_model': 'yolov8n.pt', 'epochs': 100, 'imgsz': 640, 'batch': 2, 'freeze': 10},
]


def save(value):
    value['updated_at_utc'] = datetime.now(timezone.utc).isoformat()
    pending = STATE/'state.pending.json'
    pending.write_text(json.dumps(value, indent=2), encoding='utf-8')
    os.replace(pending, STATE/'state.json')


def main():
    import msvcrt
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE/'worker.lock').open('a+b') as lock:
        lock.seek(0)
        if os.fstat(lock.fileno()).st_size == 0:
            lock.write(b'1'); lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return
        from vision.train import train
        from vision.calibrate import calibrate
        state = json.loads((STATE/'state.json').read_text()) if (STATE/'state.json').exists() else {'jobs': {}, 'plan': JOBS}
        state.update(pid=os.getpid(), phase='running', needs_agent_review=True)
        save(state)
        for job in JOBS:
            record = state['jobs'].get(job['name'], {})
            if record.get('status') == 'completed':
                continue
            suffix = uuid.uuid4().hex[:8]
            artifacts = ROOT/'vision'/('artifacts-night-'+job['name']+'-'+suffix)
            report = ROOT/'vision/reports'/('night-'+job['name']+'-'+suffix+'.json')
            record = dict(job, status='running', artifacts=str(artifacts), report=str(report))
            state['jobs'][job['name']] = record
            save(state)
            with (STATE/(job['name']+'-'+suffix+'.log')).open('w', encoding='utf-8') as log:
                try:
                    options = {k:v for k,v in job.items() if k!='name'}
                    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                        train(ROOT/'vision/data/curated-pilot-01/dataset.yaml', ROOT/'vision/data/curated-pilot-01/provenance.json', output=artifacts, device='cpu', workers=0, **options)
                        result = calibrate(artifacts, ROOT/'vision/data/curated-pilot-01/dataset.yaml', ROOT/'vision/data/curated-pilot-01/provenance.json', report, evaluate_test=False)
                    record.update(status='completed', validation=result['selected'], checkpoint_sha256=result['checkpoint_sha256'])
                except Exception as error:
                    traceback.print_exc(file=log)
                    record.update(status='failed', error=type(error).__name__+': '+str(error))
            save(state)
        state['phase'] = 'completed'
        successes = [r for r in state['jobs'].values() if r.get('status')=='completed']
        if successes:
            state['best_candidate'] = max(successes, key=lambda r:(r['validation']['f1'],r['validation']['precision']))['name']
        save(state)


if __name__=='__main__':
    os.chdir(ROOT)
    main()
