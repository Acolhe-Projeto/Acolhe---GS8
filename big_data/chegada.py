"""Landing zone (chegada/): one file per source per collection day, date in the name.

    python -B -m big_data.chegada            # collect today into big_data/chegada and check arrival

Layout (what the Databricks Volume receives in batches):
    chegada/ibge/municipios_YYYY-MM-DD.csv        IBGE Localidades, municipalities of SP
    chegada/obmigra/indicadores_YYYY-MM-DD.csv    OBMigra 2025 indicators extracted from the PDF text
    chegada/_notificacoes/notificacoes.jsonl      success/failure notifications (Airflow callbacks)
The date is the real UTC collection day, never a parameter that could backdate a batch.
"""
import argparse, csv, json, logging, os
from datetime import datetime, timezone
from pathlib import Path

LOG = logging.getLogger('acolhe.chegada')
REQUIRED = {
    'ibge': ('municipios', ['municipality_id', 'municipality', 'state_id', 'state_code', 'state', 'collected_on', 'source_sha256']),
    'obmigra': ('indicadores', ['indicator_id', 'reference_year', 'territory', 'value', 'unit', 'label_pt', 'page', 'collected_on', 'source_sha256']),
}

def today():
    return datetime.now(timezone.utc).date().isoformat()

def landing_file(root, source, day):
    prefix = REQUIRED[source][0]
    return Path(root) / source / f'{prefix}_{day}.csv'

def _write_once(path, header, rows):
    """Atomic write; an existing file for the same day is kept (immutable batch)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): return path, False
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header); w.writeheader(); w.writerows(rows)
    os.replace(tmp, path)
    return path, True

def land_ibge(chegada, snapshots, url=None, day=None, collect=None):
    if collect is None: from big_data.collect_official import collect
    day = day or today()
    manifest = collect('ibge', snapshots, url)
    folder = Path(snapshots) / 'normalized' / manifest['retrieval_day_utc']
    with (folder / 'municipalities_sp.csv').open(encoding='utf-8', newline='') as f:
        rows = [dict(r, collected_on=day, source_sha256=manifest['sha256']) for r in csv.DictReader(f)]
    path, new = _write_once(landing_file(chegada, 'ibge', day), REQUIRED['ibge'][1], rows)
    return {'source': 'ibge', 'file': path.name, 'rows': len(rows), 'new_file': new}

def land_obmigra(chegada, snapshots, url=None, day=None, collect=None, page_text=None):
    if collect is None: from big_data.collect_official import collect
    from big_data.official_integration import extract_obmigra
    day = day or today()
    manifest = collect('obmigra', snapshots, url)
    rows = extract_obmigra(Path(snapshots) / manifest['raw_path'], page_text)
    keep = REQUIRED['obmigra'][1]
    rows = [{k: r.get(k) for k in keep} | {'collected_on': day, 'source_sha256': manifest['sha256']} for r in rows]
    path, new = _write_once(landing_file(chegada, 'obmigra', day), keep, rows)
    return {'source': 'obmigra', 'file': path.name, 'rows': len(rows), 'new_file': new}

def land_from_snapshots(chegada, snapshots, day, page_text=None):
    """Rebuild a landing batch from snapshots REALLY collected on `day` (per manifests), offline.
    Raises if there was no real collection of a source that day, so batches cannot be backdated."""
    from big_data.official_integration import extract_obmigra
    out = []
    for source, sid in (('ibge', 'ibge_municipalities_sp'), ('obmigra', 'obmigra_consolidated_2025')):
        manifests = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((Path(snapshots) / 'manifests').glob(f'*_{sid}.json'))]
        that_day = [m for m in manifests if m['retrieval_day_utc'] == day]
        if not that_day: raise ValueError(f'Nenhuma coleta real de {source} em {day}')
        m = that_day[-1]
        if source == 'ibge':
            with (Path(snapshots) / 'normalized' / day / 'municipalities_sp.csv').open(encoding='utf-8', newline='') as f:
                rows = [dict(r, collected_on=day, source_sha256=m['sha256']) for r in csv.DictReader(f)]
        else:
            keep = REQUIRED['obmigra'][1]
            rows = [{k: r.get(k) for k in keep} | {'collected_on': day, 'source_sha256': m['sha256']}
                    for r in extract_obmigra(Path(snapshots) / m['raw_path'], page_text)]
        path, new = _write_once(landing_file(chegada, source, day), REQUIRED[source][1], rows)
        out.append({'source': source, 'file': path.name, 'rows': len(rows), 'new_file': new})
    return out

def check_arrival(chegada, day=None):
    """conferir_chegada: every source has today's file, non-empty, with the expected header."""
    day = day or today(); report = {}; problems = []
    for source, (_, header) in REQUIRED.items():
        path = landing_file(chegada, source, day)
        if not path.is_file(): problems.append(f'{source}: arquivo {path.name} nao chegou'); continue
        with path.open(encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f); rows = sum(1 for _ in reader)
        if reader.fieldnames != header: problems.append(f'{source}: cabecalho inesperado em {path.name}')
        elif rows == 0: problems.append(f'{source}: {path.name} vazio')
        report[source] = {'file': path.name, 'rows': rows}
    if problems: raise ValueError('; '.join(problems))
    return {'day': day, 'files': report}

def notify(chegada, event, **details):
    """Notification channel: structured log line + append-only JSONL (no personal data)."""
    record = {'at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'event': event, **details}
    folder = Path(chegada) / '_notificacoes'; folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'notificacoes.jsonl').open('a', encoding='utf-8') as f: f.write(json.dumps(record, ensure_ascii=False) + '\n')
    (LOG.error if event.endswith('failure') else LOG.info)('notificacao %s', json.dumps(record, ensure_ascii=False))
    return record

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chegada', default='big_data/chegada'); p.add_argument('--snapshots', default='big_data/official_snapshots'); a = p.parse_args()
    results = [land_ibge(a.chegada, a.snapshots), land_obmigra(a.chegada, a.snapshots)]
    print(json.dumps({'landed': results, 'conferencia': check_arrival(a.chegada)}, ensure_ascii=False, indent=2))
