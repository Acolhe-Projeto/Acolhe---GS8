import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import night_worker


class NightWorkerTests(unittest.TestCase):
    def test_state_is_saved_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(night_worker, 'STATE', Path(directory)):
                night_worker.save({'jobs': {'example': {'status': 'completed'}}})
                self.assertEqual(json.loads((Path(directory)/'state.json').read_text())['jobs']['example']['status'], 'completed')
                self.assertFalse((Path(directory)/'state.pending.json').exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows worker file locking')
    def test_duplicate_worker_exits_without_starting_jobs(self):
        import msvcrt
        with tempfile.TemporaryDirectory() as directory:
            with (Path(directory)/'worker.lock').open('w+b') as lock:
                lock.write(b'1'); lock.flush(); lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                code = 'from scripts import night_worker; from pathlib import Path; import sys; night_worker.STATE=Path(sys.argv[1]); night_worker.main()'
                result = subprocess.run([sys.executable, '-B', '-c', code, directory], capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse((Path(directory)/'state.json').exists())
