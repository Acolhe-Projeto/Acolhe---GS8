"""Convert pre-reviewed local COCO images to audited YOLO splits; never downloads."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile

from vision.audit import audit, confined, reviewed_record
from vision.service import LABELS


def prepare(annotations, images, reviews, output):
    import yaml
    from PIL import Image
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("Output already exists; choose a new directory")
    source = Path(images).resolve()
    coco = json.loads(Path(annotations).read_text(encoding="utf-8-sig"))
    metadata = json.loads(Path(reviews).read_text(encoding="utf-8-sig"))
    records = metadata.get("images") if isinstance(metadata, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("Reviews must contain a nonempty images inventory")
    image_index = {str(image["id"]): image for image in coco["images"]}
    if len(image_index) != len(coco["images"]):
        raise ValueError("Duplicate COCO image IDs")
    if len({category["id"] for category in coco["categories"]}) != len(coco["categories"]):
        raise ValueError("Duplicate COCO category IDs")
    categories = {category["id"]: list(LABELS).index(category["name"])
                  for category in coco["categories"] if category["name"] in LABELS}
    if set(categories.values()) != set(range(len(LABELS))):
        raise ValueError("COCO metadata must contain all 12 service classes")
    selected = set()
    for record in records:
        reviewed_record(record)
        if record["image_id"] in selected or record["image_id"] not in image_index:
            raise ValueError("Repeated or unknown reviewed image_id")
        selected.add(record["image_id"])
    boxes = defaultdict(list)
    for annotation in coco["annotations"]:
        image_id = str(annotation["image_id"])
        if image_id not in selected or annotation["category_id"] not in categories:
            continue
        if annotation.get("iscrowd", 0):
            raise ValueError("Review/remove crowd annotations before preparing selected images")
        image = image_index[image_id]
        width, height = image["width"], image["height"]
        x, y, w, h = annotation["bbox"]
        if (not all(type(v) in (int, float) and math.isfinite(v) for v in (x,y,w,h,width,height))
                or min(width,height,w,h) <= 0 or min(x,y) < 0 or x+w > width or y+h > height):
            raise ValueError("COCO bounding box is outside its original image")
        boxes[image_id].append((categories[annotation["category_id"]],
                               (x+w/2)/width, (y+h/2)/height, w/width, h/height))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".acolhe-curation-", dir=output.parent) as staging:
        stage = Path(staging) / "dataset"
        stage.mkdir()
        prepared = []
        for index, record in enumerate(records):
            image_info = image_index[record["image_id"]]
            image = confined(source, image_info["file_name"])
            if not boxes[record["image_id"]]:
                raise ValueError("Selected image has no target-class bounding boxes")
            with Image.open(image) as pixels:
                if pixels.size != (image_info["width"], image_info["height"]):
                    raise ValueError("Image dimensions differ from COCO annotations")
            if hashlib.sha256(image.read_bytes()).hexdigest() != record["sha256"]:
                raise ValueError("Reviewed image hash mismatch")
            # Use our own names: COCO IDs and filenames never become output paths.
            name = f"image_{index:07d}"
            relative = Path("images") / record["split"] / (name + image.suffix.lower())
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(image, target)
            label = stage / "labels" / record["split"] / (name + ".txt")
            label.parent.mkdir(parents=True, exist_ok=True)
            label.write_text("".join(" ".join(str(value) for value in box)+"\n"
                                     for box in boxes[record["image_id"]]), encoding="utf-8")
            prepared.append({**record, "file": relative.as_posix()})
        config = {"path": ".", "train": "images/train", "val": "images/val", "test": "images/test",
                  "names": list(LABELS), "nc": len(LABELS)}
        (stage / "dataset.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        metadata = {**metadata, "images": prepared,
                    "annotations_sha256": hashlib.sha256(Path(annotations).read_bytes()).hexdigest()}
        (stage / "provenance.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        report = audit(stage / "dataset.yaml", stage / "provenance.json")
        (stage / "audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        os.rename(stage, output)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True, help="Local COCO instances JSON")
    parser.add_argument("--images", required=True, help="Local directory of original images")
    parser.add_argument("--reviews", required=True, help="Reviewed per-image provenance JSON")
    parser.add_argument("--output", required=True, help="New dataset directory")
    args = parser.parse_args()
    print(json.dumps(prepare(args.annotations,args.images,args.reviews,args.output), indent=2))
