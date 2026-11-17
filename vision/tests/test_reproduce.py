import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from vision.reproduce import download


class ReproduceTests(unittest.TestCase):
    def test_exact_hash_required_before_writing_public_image(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'sample.jpg'
            response = MagicMock()
            response.__enter__.return_value.read.return_value = b'reviewed image'
            with patch('urllib.request.urlopen', return_value=response):
                with self.assertRaises(ValueError):
                    download('https://images.cocodataset.org/val2017/example.jpg', target, '0'*64)
                self.assertFalse(target.exists())
                download('https://images.cocodataset.org/val2017/example.jpg', target,
                         hashlib.sha256(b'reviewed image').hexdigest())
            self.assertEqual(target.read_bytes(), b'reviewed image')

    def test_nonpublic_source_is_rejected_without_network(self):
        with patch('urllib.request.urlopen') as request:
            with self.assertRaises(ValueError):
                download('http://127.0.0.1/private', Path('unused'), '0'*64)
        request.assert_not_called()
