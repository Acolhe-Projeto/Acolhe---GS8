import unittest
import tempfile
import hashlib
import json
from pathlib import Path
from vision.calibrate import score, activate
from vision.service import inference_options


class CalibrationTests(unittest.TestCase):
    def test_activation_is_bound_to_checkpoint_and_changes_only_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'best.pt').write_bytes(b'fixture')
            digest = hashlib.sha256(b'fixture').hexdigest()
            path = root/'model_manifest.json'
            path.write_text(json.dumps({'checkpoint_sha256': digest, 'quality_validated': False}))
            report = {'checkpoint_sha256': 'wrong', 'selected': {'confidence': .1}, 'imgsz': 640, 'selection_rule': 'validation F1'}
            with self.assertRaises(ValueError):
                activate(root, report)
            self.assertNotIn('inference', json.loads(path.read_text()))
            report['checkpoint_sha256'] = digest
            activate(root, report)
            manifest = json.loads(path.read_text())
            self.assertEqual(manifest['inference'], {'conf': .1, 'imgsz': 640})
            self.assertFalse(manifest['quality_validated'])

    def test_manifest_limits_and_legacy_defaults(self):
        self.assertEqual(inference_options({}), {'conf': .5, 'imgsz': 320})
        self.assertEqual(inference_options({'inference': {'conf': .15, 'imgsz': 640}}), {'conf': .15, 'imgsz': 640})
        for options in [{'conf': float('nan'), 'imgsz': 640}, {'conf': True, 'imgsz': 640},
                        {'conf': .1, 'imgsz': 641}, {'conf': .1, 'imgsz': 4096}, None]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                inference_options({'inference': options})

    def test_duplicate_and_wrong_class_are_false_positives(self):
        gold = [{'class_id': 0, 'xyxy': [0, 0, 10, 10]}]
        predictions = [{'class_id': cls, 'xyxy': [0, 0, 10, 10], 'confidence': c}
                       for cls, c in [(0, .9), (0, .8), (1, .7)]]
        result = score([{'gold': gold, 'predictions': predictions}], .5)
        self.assertEqual((result['tp'], result['fp'], result['fn']), (1, 2, 0))

    def test_threshold_and_localization_misses_remain_false_negatives(self):
        gold = [{'class_id': 0, 'xyxy': [0, 0, 10, 10]}]
        image = {'gold': gold, 'predictions': [{'class_id': 0, 'xyxy': [0, 0, 10, 10], 'confidence': .2}]}
        self.assertEqual(score([image], .5)['fn'], 1)
        self.assertEqual(score([image], .1)['recall'], 1)
        image['predictions'][0]['xyxy'] = [8, 8, 18, 18]
        self.assertEqual(score([image], .1)['tp'], 0)
