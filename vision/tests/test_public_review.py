import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from vision.public_review import approve, build, fingerprint, flickr_credit, clear_targets


class PublicReviewTests(unittest.TestCase):
    def test_flickr_current_author_and_license_required(self):
        item = {"@type": "ImageObject", "license": "https://creativecommons.org/licenses/by/2.0/",
                "author": {"name": "Example photographer", "url": "https://flickr.com/photos/example"}}
        html = '<script type="application/ld+json">'+json.dumps({"@graph": [item]})+'</script>'
        self.assertEqual(flickr_credit(html)["author"], "Example photographer")
        with self.assertRaises(ValueError): flickr_credit(html.replace("licenses/by/", "licenses/by-nc/"))
        with self.assertRaises(ValueError): flickr_credit('<script type="application/ld+json">{broken}</script>')

    def test_simple_objects_counts_visible_primary_targets_not_tiny_background(self):
        image={'width':800,'height':400}
        categories={1:'fork',2:'book',3:'bottle'}
        boxes=[{'category_id':1,'bbox':[0,0,200,20]},
               {'category_id':2,'bbox':[0,0,20,40]},
               {'category_id':3,'bbox':[0,0,200,100]}]
        self.assertEqual(clear_targets(image,boxes,categories),['bottle','fork'])

    def packet(self, root):
        image = root / "image.jpg"; image.write_bytes(b"test-only-image")
        record = {"image_id": "1", "file": "image.jpg", "split": "train", "source_url": "https://example.org/photo/1",
                  "sha256": hashlib.sha256(image.read_bytes()).hexdigest(), "author": "Example author",
                  "license": "https://creativecommons.org/licenses/by/2.0/", "privacy_reviewed": False}
        digest = fingerprint([record])
        (root / "reviews.json").write_text(json.dumps({"packet_sha256": digest, "images": [record]}), encoding="utf-8")
        return digest

    def test_explicit_approval_is_bound_to_exact_packet_and_pixels(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); digest = self.packet(root)
            with self.assertRaises(ValueError): approve(root, "wrong", "test reviewer", "test authorization")
            with self.assertRaises(ValueError): approve(root, digest, "", "test authorization")
            path = approve(root, digest, "test reviewer", "test authorization")
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertTrue(data["images"][0]["privacy_reviewed"])
            self.assertFalse(json.loads((root / "reviews.json").read_text())["images"][0]["privacy_reviewed"])
            with self.assertRaises(FileExistsError): approve(root, digest, "test reviewer", "test authorization")

    def test_changed_image_cannot_reuse_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); digest = self.packet(root)
            (root / "image.jpg").write_bytes(b"changed")
            with self.assertRaises(ValueError): approve(root, digest, "test reviewer", "test authorization")
            self.assertFalse((root / "reviews.approved.json").exists())

    def test_manual_annotations_are_bound_to_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.packet(root)
            annotation = root / "instances_subset.json"
            annotation.write_text('{"bbox":[1,2,3,4]}', encoding="utf-8")
            annotation_hash = hashlib.sha256(annotation.read_bytes()).hexdigest()
            path = root / "reviews.json"; review = json.loads(path.read_text())
            review["annotations_sha256"] = annotation_hash; review["annotations_file"] = annotation.name
            for record in review["images"]: record["annotations_sha256"] = annotation_hash
            review["packet_sha256"] = fingerprint(review["images"])
            path.write_text(json.dumps(review), encoding="utf-8")
            annotation.write_text('{"bbox":[5,6,7,8]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Annotations changed"):
                approve(root, review["packet_sha256"], "test reviewer", "test authorization")
            self.assertFalse((root / "reviews.approved.json").exists())

    def test_invalid_counts_fail_before_network(self):
        with self.assertRaises(ValueError): build("unused", train=0)

    def test_cached_batch_does_not_discard_images_needed_by_later_splits(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "originals").mkdir(); (root / "source-records").mkdir()
            images, annotations = [], []
            for index in range(6):
                image_id = index + 1; filename = f"{image_id:012d}.jpg"
                image = root / "originals" / filename
                Image.new("RGB", (8, 8), (index*30, 10, 20)).save(image)
                label = "book" if index < 3 else "bus"
                images.append({"id": image_id, "file_name": filename, "license": 4, "width": 8, "height": 8,
                               "flickr_url": f"https://example.org/{image_id}_test.jpg"})
                annotations.append({"id": image_id, "image_id": image_id, "category_id": 1 if label == "book" else 2,
                                    "bbox": [0, 0, 8, 8], "iscrowd": 0})
                record = {"image_id": str(image_id), "file": "originals/"+filename,
                          "sha256": hashlib.sha256(image.read_bytes()).hexdigest(), "target_classes": [label],
                          "source_url": "https://example.org/photo/"+str(image_id), "author": "Test author",
                          "author_url": "https://example.org/author", "license": "https://creativecommons.org/licenses/by/2.0/",
                          "person_annotations": 0, "privacy_reviewed": False}
                (root / "source-records" / f"{image_id}.json").write_text(json.dumps(record), encoding="utf-8")
            coco = {"images": images, "annotations": annotations,
                    "categories": [{"id": 1, "name": "book"}, {"id": 2, "name": "bus"}]}
            with patch("vision.public_review.LABELS", {"book": {}, "bus": {}}), patch("vision.public_review.metadata", side_effect=[coco, {"annotations": []}]), patch("vision.public_review.fetch") as network:
                summary = build(root, train=1, val=1, test=1, cached_only=True)
            network.assert_not_called()
            self.assertEqual(summary["images"], 6)
            self.assertEqual(summary["privacy_reviewed_true"], 0)
            for split in ("train", "val", "test"):
                self.assertEqual(summary["class_images_per_split"][split], {"book": 1, "bus": 1})


            # A fresh packet can allocate only train/validation and enforce image totals.
            import shutil
            expanded = root / "expansion"
            expanded.mkdir()
            shutil.copytree(root / "source-records", expanded / "source-records")
            shutil.copytree(root / "originals", expanded / "originals")
            with patch("vision.public_review.LABELS", {"book": {}, "bus": {}}), patch("vision.public_review.metadata", side_effect=[coco, {"annotations": []}]), patch("vision.public_review.fetch") as network:
                summary = build(expanded, train=1, val=1, test=0, cached_only=True,
                                source_split="train2017", minimum_train_images=3, minimum_val_images=2)
            network.assert_not_called()
            self.assertGreaterEqual(summary["split_images"]["train"], 3)
            self.assertGreaterEqual(summary["split_images"]["val"], 2)
            self.assertNotIn("test", summary["split_images"])
            review = json.loads((expanded / "reviews.json").read_text(encoding="utf-8"))
            self.assertEqual(review["annotations_sha256"], hashlib.sha256((expanded / "instances_subset.json").read_bytes()).hexdigest())


if __name__ == "__main__": unittest.main()
