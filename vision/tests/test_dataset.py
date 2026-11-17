"""Synthetic unit fixtures validate guards, never count as training evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from unittest.mock import Mock

from vision import train
from vision.audit import audit
from vision.prepare import prepare
from vision.service import LABELS
from vision import service


@unittest.skipUnless(importlib.util.find_spec("yaml") and importlib.util.find_spec("PIL"),
                     "Install vision/requirements-data.txt for image audit tests")
class DatasetTests(unittest.TestCase):
    def setUp(self):
        import yaml
        from PIL import Image
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "dataset.yaml"
        self.provenance = self.root / "provenance.json"
        self.config = {"path": ".", "train": "images/train", "val": "images/val", "test": "images/test", "names": list(LABELS)}
        self.data.write_text(yaml.safe_dump(self.config), encoding="utf-8")
        self.records = []
        for s, split in enumerate(("train", "val", "test")):
            for i, name in enumerate(LABELS):
                image = self.root / "images" / split / f"{i}.png"
                image.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (8, 8), (s*50, i*10, 70)).save(image)
                label = self.root / "labels" / split / f"{i}.txt"
                label.parent.mkdir(parents=True, exist_ok=True)
                label.write_text(f"{i} 0.5 0.5 0.5 0.5\n")
                self.records.append({"image_id": f"{split}-{i}", "file": image.relative_to(self.root).as_posix(),
                                     "split": split, "source_url": "https://example.org/fixture",
                                     "author": "Synthetic unit test", "license": "test fixture only",
                                     "reviewed_at": "2026-11-16", "privacy_reviewed": True,
                                     "sha256": hashlib.sha256(image.read_bytes()).hexdigest()})
        self.metadata = dict(real_images=True, source_url="https://example.org/fixture",
                             license="test only", split_method="explicit fixture splits",
                             class_names=list(LABELS), images=self.records)
        self.save_inventory()

    def save_inventory(self):
        self.provenance.write_text(json.dumps(self.metadata), encoding="utf-8")

    def test_complete_audit_counts_and_fingerprint(self):
        result = audit(self.data, self.provenance)
        self.assertEqual(result["splits"]["test"]["images"], 12)
        self.assertEqual(result["splits"]["train"]["objects_per_class"], dict.fromkeys(LABELS, 1))
        self.assertFalse(result["quality_validated"])
        old_signature = result["dataset_fingerprint_sha256"]
        label = self.root / "labels/train/0.txt"
        label.write_text("0 0.4 0.4 0.3 0.3\n")
        self.assertNotEqual(audit(self.data,self.provenance)["dataset_fingerprint_sha256"], old_signature)

    def test_duplicate_pixels_rejected_even_with_distinct_ids(self):
        source = self.root / self.records[0]["file"]
        target = self.root / self.records[12]["file"]
        target.write_bytes(source.read_bytes())
        self.records[12]["sha256"] = self.records[0]["sha256"]
        self.save_inventory()
        with self.assertRaisesRegex(ValueError, "Duplicate image content"):
            audit(self.data, self.provenance)

    def test_tampering_missing_reviews_and_inventory_rejected(self):
        self.records[0]["privacy_reviewed"] = False
        self.save_inventory()
        with self.assertRaisesRegex(ValueError, "privacy review"):
            audit(self.data,self.provenance)
        self.records[0]["privacy_reviewed"] = True
        self.records[0]["sha256"] = "0" * 64
        self.save_inventory()
        with self.assertRaisesRegex(ValueError, "hash"):
            audit(self.data,self.provenance)

    def test_invalid_boxes_and_missing_class_rejected(self):
        label = self.root / "labels/train/0.txt"
        for contents in ("0 nan 0.5 0.5 0.5", "12 0.5 0.5 0.5 0.5", "0 0.1 0.5 0.5 0.5", ""):
            label.write_text(contents)
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                audit(self.data,self.provenance)

    def test_path_escape_or_download_rejected(self):
        import yaml
        for change in ({"train":"../outside"}, {"download":"arbitrary command"}):
            self.data.write_text(yaml.safe_dump({**self.config,**change}))
            with self.assertRaises(ValueError):
                audit(self.data,self.provenance)

    def test_prepare_coco_roundtrip_and_exclusive_output(self):
        images, annotations = [], []
        for i, record in enumerate(self.records):
            images.append({"id":record["image_id"], "file_name":record["file"], "width":8,"height":8})
            annotations.append({"image_id":record["image_id"], "category_id":i%12,
                                "bbox":[2,2,4,4],"iscrowd":0})
        coco = self.root/"instances.json"
        coco.write_text(json.dumps({"images":images,"annotations":annotations,
                                    "categories":[{"id":i,"name":name} for i,name in enumerate(LABELS)]}))
        output = self.root / "prepared"
        result = prepare(coco,self.root,self.provenance,output)
        self.assertTrue(result["passed"])
        self.assertEqual(audit(output/"dataset.yaml",output/"provenance.json"),result)
        with self.assertRaises(FileExistsError):
            prepare(coco,self.root,self.provenance,output)

    def test_failed_preparation_leaves_no_output(self):
        coco = self.root/"instances.json"
        coco.write_text(json.dumps({"images":[],"annotations":[],"categories":[]}))
        output = self.root/"prepared"
        with self.assertRaises(ValueError): prepare(coco,self.root,self.provenance,output)
        self.assertFalse(output.exists())

    def test_malformed_image_never_reaches_prediction(self):
        with patch.object(service,"_load_verified_model",return_value=Mock()) as loader:
            with self.assertRaisesRegex(ValueError,"Invalid or unsafe image"):
                service.predict(b"not an image")
            loader.return_value.predict.assert_not_called()

    def test_image_inference_is_cpu_and_does_not_save_upload(self):
        model = Mock()
        model.predict.return_value = []
        with patch.object(service,"_load_verified_model",return_value=model):
            result = service.predict((self.root/self.records[0]["file"]).read_bytes())
        self.assertEqual(model.predict.call_args.kwargs["device"],"cpu")
        self.assertFalse(model.predict.call_args.kwargs["save"])
        self.assertFalse(result["stores_image"])
        self.assertEqual(result["detections"],[])

    def test_optional_image_decoder_failure_is_an_invalid_upload(self):
        model = Mock()
        with patch.object(service,"_load_verified_model",return_value=model), patch("PIL.Image.open",side_effect=ModuleNotFoundError("pi_heif")):
            with self.assertRaisesRegex(ValueError,"Invalid or unsafe image"):
                service.predict(b"invalid image")
        model.predict.assert_not_called()

    def test_cpu_training_contract_records_audit_and_test_metrics(self):
        import yaml
        checkpoint = self.root / "trusted-test-checkpoint.pt"
        checkpoint.write_bytes(b"unit-test placeholder, not a model")
        model = Mock()
        model.trainer.best = checkpoint
        evaluation = Mock()
        evaluation.results_dict = {"metrics/mAP50(B)":0.42}
        evaluation.save_dir = "unit-test-evaluation"
        evaluation.box.ap_class_index = [0]
        evaluation.box.p = [0.6]; evaluation.box.r = [0.7]
        evaluation.box.ap50 = [0.42]; evaluation.box.ap = [0.25]
        model.val.return_value = evaluation
        runtime = Mock(); runtime.YOLO.return_value = model
        out = self.root / "artifacts"
        with patch.dict("sys.modules", {"ultralytics":runtime}):
            result = train.train(self.data,self.provenance,epochs=1,output=out)
        self.assertEqual(model.train.call_args.kwargs["device"], "cpu")
        self.assertEqual(model.train.call_args.kwargs["imgsz"],320)
        self.assertEqual(model.train.call_args.kwargs["workers"],0)
        self.assertEqual(model.val.call_args.kwargs["split"],"test")
        resolved = yaml.safe_load((out/"dataset-resolved.yaml").read_text())
        self.assertEqual(Path(resolved["path"]),self.root)
        self.assertEqual(result["per_class_metrics"]["backpack"]["map50"],0.42)
        self.assertFalse(result["quality_validated"])
        self.assertTrue((out/"error_analysis.md").is_file())
        # Deferring test evaluation must not instantiate a test model or call val.
        model.reset_mock(); runtime.YOLO.reset_mock()
        with patch.dict("sys.modules", {"ultralytics":runtime}):
            deferred = train.train(self.data,self.provenance,epochs=1,output=self.root/"deferred",evaluate_test=False)
        model.val.assert_not_called()
        runtime.YOLO.assert_called_once_with("yolo11n.pt")
        self.assertIsNone(deferred["test_metrics"])
        self.assertEqual(deferred["per_class_metrics"], {})



    def test_warm_start_checks_hash_and_uses_explicit_low_rate(self):
        from types import SimpleNamespace
        parent = self.root / "parent"
        parent.mkdir()
        checkpoint = parent / "best.pt"
        checkpoint.write_bytes(b"unit fixture, never a trained-model claim")
        manifest = {"class_names":list(LABELS), "trained_on_real_images":True,
                    "checkpoint_sha256":hashlib.sha256(checkpoint.read_bytes()).hexdigest(), "model":"yolo26n", "epochs":80, "imgsz":640}
        (parent/"model_manifest.json").write_text(json.dumps(manifest))
        runtime = Mock(); model = runtime.YOLO.return_value
        model.names = dict(enumerate(LABELS)); model.trainer.best = checkpoint; model.trainer.epoch = 8
        with patch.dict("sys.modules", {"ultralytics":runtime}):
            result = train.train(self.data,self.provenance,epochs=30,output=self.root/"warm",base_model="yolo26n.pt",
                                 initial_artifacts=parent,learning_rate=5e-5,patience=8,mosaic=0,freeze=10,evaluate_test=False)
        runtime.YOLO.assert_called_once_with(str(checkpoint))
        kwargs=model.train.call_args.kwargs
        self.assertEqual((kwargs['optimizer'],kwargs['lr0'],kwargs['warmup_bias_lr']), ('AdamW',5e-5,0.0))
        self.assertFalse(kwargs['resume']); model.val.assert_not_called()
        self.assertEqual(result['epochs_completed'],9)
        self.assertEqual(result['warm_start']['checkpoint_sha256'],manifest['checkpoint_sha256'])
        from vision.calibrate import calibrate
        with patch.dict("sys.modules", {"ultralytics":runtime}), patch("vision.calibrate.collect",return_value=[]) as collect:
            calibration=calibrate(parent,self.data,self.provenance,self.root/"calibration.json",imgsz=960)
        self.assertEqual(calibration['imgsz'],960)
        self.assertEqual(calibration['trained_imgsz'],640)
        self.assertEqual(collect.call_args.args[-1],960)
        checkpoint.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"hash"):
            train.initial_checkpoint(parent,"yolo26n.pt")

    def test_merge_deduplicates_without_changing_splits_or_labels(self):
        from vision.merge_approved import merge
        result = merge([self.root,self.root], self.root, self.root/"merged")
        self.assertEqual([result['splits'][s]['images'] for s in ('train','val','test')], [12,12,12])
        merged=json.loads((self.root/"merged/provenance.json").read_text(encoding='utf-8'))
        original={r['image_id']:r for r in self.records}
        for record in merged['images']:
            old=original[record['image_id']]
            self.assertEqual(old['split'],record['split'])
            self.assertEqual(old['sha256'],record['sha256'])
        with self.assertRaises(FileExistsError): merge([self.root],self.root,self.root/"merged")
        import shutil
        other=self.root/"other"
        other.mkdir()
        shutil.copytree(self.root/"images",other/"images")
        shutil.copytree(self.root/"labels",other/"labels")
        shutil.copyfile(self.data,other/"dataset.yaml")
        shutil.copyfile(self.provenance,other/"provenance.json")
        label=other/"labels/train/0.txt"
        label.write_text("0 0.4 0.4 0.3 0.3\n")
        with self.assertRaisesRegex(ValueError,"Conflicting"):
            merge([self.root,other],self.root,self.root/"conflict")
        self.assertFalse((self.root/"conflict").exists())



class TrainingOptionsTests(unittest.TestCase):
    def test_invalid_cpu_options_fail_before_data_or_runtime(self):
        for options in ({"imgsz":33},{"batch":0},{"workers":-1},{"device":""},{"base_model":"https://untrusted.invalid/model.pt"},{"freeze":-1},{"freeze":23},{"learning_rate":0},{"learning_rate":float("nan")},{"patience":0},{"mosaic":-1}):
            with self.subTest(options=options), patch.object(train,"validate_dataset") as validate:
                with self.assertRaises(ValueError): train.train("missing","missing",**options)
                validate.assert_not_called()
