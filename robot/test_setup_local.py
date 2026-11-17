import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from robot import setup_local


class SetupTests(unittest.TestCase):
    def test_incomplete_voice_package_is_rejected_before_copying(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'source'; destination=root/'repo'
            (source/'modelos/whisper-small').mkdir(parents=True)
            (source/'modelos/whisper-small/model.bin').touch()
            (source/'piper').mkdir()
            (source/'piper/piper.exe').touch()
            (source/'piper/pt_BR-faber-medium.onnx.json').write_text('{}')
            with patch.object(setup_local,'ROOT',destination),patch('sys.argv',['setup_local','--source',str(source)]),contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught: setup_local.main()
            self.assertEqual(caught.exception.code,2)
            self.assertFalse((destination/'robot/.models').exists())
