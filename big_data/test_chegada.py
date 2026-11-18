import csv, json, tempfile, unittest
from pathlib import Path
from big_data.chegada import land_ibge, land_obmigra, check_arrival, notify, landing_file, REQUIRED
from big_data.collect_official import save_snapshot
from big_data.test_official_integration import PAGES

def fake_collect(snapshots):
    def collect(source, root, url=None):
        if source == 'ibge':
            m = save_snapshot(root, {'id': 'ibge_municipalities_sp', 'url': url or 'https://x/ibge', 'extension': 'json'}, b'[]', {'status': 200})
            folder = Path(root) / 'normalized' / m['retrieval_day_utc']; folder.mkdir(parents=True, exist_ok=True)
            with (folder / 'municipalities_sp.csv').open('w', newline='', encoding='utf-8') as f:
                w = csv.writer(f); w.writerow(['municipality_id', 'municipality', 'state_id', 'state_code', 'state'])
                w.writerow([3550308, 'Sao Paulo', 35, 'SP', 'Sao Paulo'])
            return m
        return save_snapshot(root, {'id': 'obmigra_consolidated_2025', 'url': 'https://x/o.pdf', 'extension': 'pdf'}, b'%PDF-x', {'status': 200})
    return collect

class ChegadaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.chegada, self.snap = self.root / 'chegada', self.root / 'snap'
        self.collect = fake_collect(self.snap)

    def tearDown(self): self.tmp.cleanup()

    def land(self, day):
        return (land_ibge(self.chegada, self.snap, day=day, collect=self.collect),
                land_obmigra(self.chegada, self.snap, day=day, collect=self.collect, page_text=lambda n: PAGES.get(n, '')))

    def test_one_file_per_source_with_date_in_name(self):
        ibge, obm = self.land('2026-11-17')
        self.assertEqual(ibge['file'], 'municipios_2026-11-17.csv'); self.assertEqual(obm['file'], 'indicadores_2026-11-17.csv')
        self.assertEqual(obm['rows'], 7)
        result = check_arrival(self.chegada, '2026-11-17')
        self.assertEqual(result['files']['ibge']['rows'], 1)

    def test_same_day_batch_is_immutable(self):
        self.land('2026-11-17'); before = landing_file(self.chegada, 'ibge', '2026-11-17').read_bytes()
        ibge, _ = self.land('2026-11-17')
        self.assertFalse(ibge['new_file']); self.assertEqual(before, landing_file(self.chegada, 'ibge', '2026-11-17').read_bytes())

    def test_check_arrival_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, 'nao chegou'): check_arrival(self.chegada, '2026-11-18')
        self.land('2026-11-18')
        path = landing_file(self.chegada, 'obmigra', '2026-11-18'); path.write_text(','.join(REQUIRED['obmigra'][1]) + '\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'vazio'): check_arrival(self.chegada, '2026-11-18')
        path.write_text('a,b\n1,2\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'cabecalho'): check_arrival(self.chegada, '2026-11-18')

    def test_notification_is_appended(self):
        notify(self.chegada, 'task_failure', task_id='coletar_ibge'); notify(self.chegada, 'chegada_ok', day='2026-11-17')
        lines = [json.loads(l) for l in (self.chegada / '_notificacoes' / 'notificacoes.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual([l['event'] for l in lines], ['task_failure', 'chegada_ok'])

    def test_only_https_sources(self):
        from big_data.collect_official import collect
        with self.assertRaisesRegex(ValueError, 'https'): collect('ibge', self.snap, 'http://insecure.example')
