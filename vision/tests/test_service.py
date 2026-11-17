import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from vision import service

class VisionTests(unittest.TestCase):
    def test_status_has_readiness(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(service, "MODEL", Path(directory) / "missing.pt"):
                self.assertFalse(service.status()["ready"])
    def test_missing_model_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(service, "MODEL", Path(directory) / "missing.pt"):
                with self.assertRaises(service.ModelUnavailable):
                    service.predict(b"not an image")
    def test_classes_are_educational(self):
        self.assertEqual(len(service.LABELS), 12)
        self.assertEqual(service.LABELS["backpack"]["es"], "mochila")
