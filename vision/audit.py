"""Audit a curated YOLO dataset before importing the training stack; no downloads."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlparse

from vision.service import LABELS
from vision.train import load_dataset_config, validate_dataset

SPLITS = ("train", "val", "test")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def reviewed_record(record):
    if not isinstance(record, dict) or record.get("privacy_reviewed") is not True:
        raise ValueError("Every image needs a recorded human privacy review")
    for key in ("image_id", "source_url", "license", "author", "reviewed_at", "sha256", "split"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError("Missing image provenance: " + key)
    url = urlparse(record["source_url"])
    if url.scheme not in ("https", "http") or not url.netloc:
        raise ValueError("Image source_url must be the original HTTP(S) source")
    datetime.fromisoformat(record["reviewed_at"].replace("Z", "+00:00"))
    if record["split"] not in SPLITS:
        raise ValueError("Image split must be train, val or test")
    digest = record["sha256"]
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Image sha256 must be a lowercase SHA-256 digest")


def confined(root, value):
    result = (root / value).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError("Dataset paths must stay inside the dataset root")
    return result


def audit(dataset, provenance):
    data, metadata = validate_dataset(dataset, provenance)
    _, config = load_dataset_config(data)
    if "download" in config:
        raise ValueError("Automatic download directives are not permitted in curated datasets")
    root_value = config.get("path", ".")
    if not isinstance(root_value, str):
        raise ValueError("Dataset path must be a string")
    root = (data.parent / root_value).resolve()
    records = metadata.get("images")
    if not isinstance(records, list) or not records:
        raise ValueError("Provenance needs a nonempty per-image images inventory")
    inventory = {}
    image_ids = set()
    for record in records:
        reviewed_record(record)
        filename = record.get("file")
        if not isinstance(filename, str) or not filename:
            raise ValueError("Every image needs a dataset-relative file path")
        path = confined(root, filename)
        if path in inventory or record["image_id"] in image_ids:
            raise ValueError("Repeated inventory file or image_id")
        inventory[path] = record
        image_ids.add(record["image_id"])
    from PIL import Image
    seen_hashes, seen_files = set(), set()
    split_counts, fingerprints = {}, []
    for split in SPLITS:
        value = config[split]
        if not isinstance(value, str):
            raise ValueError("Audited splits must be image directory paths")
        folder = confined(root, value)
        if not folder.is_dir() or folder.parent.name != "images":
            raise ValueError("Each split must be a directory directly under images/")
        label_folder = folder.parent.parent / "labels" / folder.name
        paths = sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
        if not paths:
            raise ValueError("Empty image split: " + split)
        boxes, class_images, expected_labels = Counter(), Counter(), set()
        for image in paths:
            if image.is_symlink() or not image.resolve().is_relative_to(folder):
                raise ValueError("Images must not link outside their split")
            image = image.resolve()
            if image in seen_files:
                raise ValueError("Image occurs in more than one split")
            seen_files.add(image)
            record = inventory.get(image)
            if record is None or record["split"] != split:
                raise ValueError("Missing or wrong-split image inventory: " + image.name)
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if digest != record["sha256"]:
                raise ValueError("Image hash does not match inventory: " + image.name)
            if digest in seen_hashes:
                raise ValueError("Duplicate image content within/across splits")
            seen_hashes.add(digest)
            with Image.open(image) as source:
                if source.width * source.height > 20_000_000:
                    raise ValueError("Image exceeds 20 megapixels")
                source.verify()
            label = label_folder / image.relative_to(folder).with_suffix(".txt")
            if label.is_symlink() or not label.resolve().is_relative_to(root):
                raise ValueError("Label must stay inside dataset root")
            if label in expected_labels:
                raise ValueError("Two images would share one label file")
            expected_labels.add(label)
            classes = set()
            for line in label.read_text(encoding="utf-8-sig").splitlines():
                parts = line.split()
                if len(parts) != 5:
                    raise ValueError("YOLO labels need class x_center y_center width height")
                class_id = int(parts[0])
                if str(class_id) != parts[0] or not 0 <= class_id < len(LABELS):
                    raise ValueError("YOLO class ID outside 0..11")
                x, y, w, h = map(float, parts[1:])
                if (not all(math.isfinite(v) for v in (x, y, w, h)) or
                        not 0 < w <= 1 or not 0 < h <= 1 or
                        x-w/2 < -1e-6 or x+w/2 > 1+1e-6 or
                        y-h/2 < -1e-6 or y+h/2 > 1+1e-6):
                    raise ValueError("YOLO boxes must be finite, positive and inside the image")
                name = list(LABELS)[class_id]
                boxes[name] += 1
                classes.add(name)
            class_images.update(classes)
            fingerprints.append((image.relative_to(root).as_posix(), digest,
                                 hashlib.sha256(label.read_bytes()).hexdigest()))
        if {p for p in label_folder.rglob("*.txt")} != expected_labels:
            raise ValueError("Orphan label files in split: " + split)
        missing = set(LABELS) - set(boxes)
        if missing:
            raise ValueError("Classes without boxes in " + split + ": " + ", ".join(sorted(missing)))
        split_counts[split] = {"images": len(paths), "objects": sum(boxes.values()),
                               "objects_per_class": dict(boxes), "images_per_class": dict(class_images)}
    if set(inventory) != seen_files:
        raise ValueError("Inventory contains images absent from the dataset splits")
    signature = hashlib.sha256(json.dumps(sorted(fingerprints), ensure_ascii=False).encode()).hexdigest()
    return {"passed": True, "class_names": list(LABELS), "splits": split_counts,
            "dataset_fingerprint_sha256": signature, "duplicate_content": 0,
            "license_review": "human declarations checked; legal rights not independently verified",
            "perceptual_duplicates_checked": False, "quality_validated": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--provenance", required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.dataset, args.provenance), indent=2, ensure_ascii=False))
