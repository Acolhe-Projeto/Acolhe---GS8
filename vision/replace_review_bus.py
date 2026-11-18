"""Create a fresh proposal replacing the mislabeled tram; no approval or training."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

from vision.audit import confined
from vision.public_review import fingerprint, publish_review
from vision.service import LABELS

NEW_ID = 900000001
REMOVED_ID = "514376"
# Proposed from visual inspection in ORIGINAL 4496x3000 pixels, including mirrors/wheels.
BUS_BOX = [720, 1040, 3408, 1296]


def replace(source, target, image_path, metadata_path):
    from PIL import Image, ImageDraw
    source, target = Path(source).resolve(), Path(target).resolve()
    if target.exists(): raise FileExistsError("Choose a new review packet directory")
    old = json.loads((source / "reviews.json").read_text(encoding="utf-8"))
    if old.get("human_approval") != "pending": raise ValueError("Do not silently replace an approved dataset")
    if fingerprint(old["images"]) != old["packet_sha256"]: raise ValueError("Source review packet changed")
    info = next(iter(json.loads(Path(metadata_path).read_text(encoding="utf-8"))["query"]["pages"].values()))["imageinfo"][0]
    rights = info["extmetadata"]
    if info["descriptionurl"] != "https://commons.wikimedia.org/wiki/File:Burlington_Trailways_bus.jpg" or "Znns" not in rights["Artist"]["value"]:
        raise ValueError("Manual annotation and attribution apply only to the selected Commons photo")
    if rights["LicenseShortName"]["value"] != "CC BY 4.0" or rights["LicenseUrl"]["value"].rstrip("/") != "https://creativecommons.org/licenses/by/4.0":
        raise ValueError("Unexpected Commons image license")
    pixels = Path(image_path).read_bytes()
    if hashlib.sha1(pixels).hexdigest() != info["sha1"]:
        raise ValueError("Commons API SHA-1 does not match original pixels")
    with Image.open(image_path) as image:
        if image.size != (4496, 3000) or image.size != (info["width"], info["height"]):
            raise ValueError("Manual annotation applies only to the reviewed original dimensions")
    records = []
    for original in old["images"]:
        record = dict(original)
        if record["image_id"] == REMOVED_ID:
            record = {"image_id": str(NEW_ID), "file": "originals/commons-burlington-bus.jpg", "split": original["split"],
                      "review_number": original["review_number"], "source_url": info["descriptionurl"],
                      "download_url": info["url"], "author": "Znns", "author_url": "https://commons.wikimedia.org/wiki/User:Znns",
                      "license": "https://creativecommons.org/licenses/by/4.0/", "sha256": hashlib.sha256(pixels).hexdigest(),
                      "source_metadata_sha256": hashlib.sha256(Path(metadata_path).read_bytes()).hexdigest(),
                      "source_checked_at": datetime.now(timezone.utc).isoformat(),
                      "license_verification": "Commons imageinfo declares author Znns and CC-BY4.0; human legal review pending",
                      "privacy_reviewed": False, "reviewed_at": "", "target_classes": ["bus"], "person_annotations": 0,
                      "person_annotation_source": "Agent visual screening; no person annotations supplied by Commons",
                      "source_dataset": "Wikimedia Commons", "annotation_method": "manual_agent_bbox",
                      "annotation_review": "pending_human", "proposed_bbox_xywh": BUS_BOX,
                      "captions": ["One complete red Burlington Trailways road coach; no visible people in agent screening."]}
        if record["image_id"] == "393226": record["split"] = "test"
        record["privacy_reviewed"] = False; record["reviewed_at"] = ""
        for key in ("reviewer", "approval_reference"): record.pop(key, None)
        records.append(record)
    if len(records) != 40 or not any(record["image_id"] == str(NEW_ID) for record in records):
        raise ValueError("Expected the exact original 40-image review packet")
    dataset = json.loads((source / "instances_val2017.json").read_text(encoding="utf-8"))
    kept = {int(record["image_id"]) for record in records}
    dataset["images"] = [image for image in dataset["images"] if image["id"] in kept]
    dataset["annotations"] = [annotation for annotation in dataset["annotations"] if annotation["image_id"] in kept]
    bus_id = next(category["id"] for category in dataset["categories"] if category["name"] == "bus")
    dataset["images"].append({"id": NEW_ID, "file_name": "commons-burlington-bus.jpg", "width": 4496, "height": 3000,
                              "source_url": info["descriptionurl"], "source_dataset": "Wikimedia Commons"})
    dataset["annotations"].append({"id": NEW_ID, "image_id": NEW_ID, "category_id": bus_id, "bbox": BUS_BOX,
                                   "area": BUS_BOX[2]*BUS_BOX[3], "iscrowd": 0,
                                   "annotation_method": "manual_agent_bbox", "human_review": "pending"})
    annotation_bytes = json.dumps(dataset, indent=2, ensure_ascii=False).encode()
    annotation_hash = hashlib.sha256(annotation_bytes).hexdigest()
    for record in records: record["annotations_sha256"] = annotation_hash
    review = {**old, "images": records, "human_approval": "pending", "packet_sha256": fingerprint(records),
              "annotations_file": "instances_subset.json", "annotations_sha256": annotation_hash,
              "license": "39 COCO photographs CC-BY2.0; one Commons photograph CC-BY4.0; original COCO annotations CC-BY4.0; proposed agent bbox awaiting review",
              "split_method": "Previous untrained pilot; replace tram with Commons bus; move ID393226 train to test to retain traffic-light coverage; before augmentation/training",
              "previous_packet_sha256": old["packet_sha256"], "removed_image_ids": [REMOVED_ID],
              "manual_annotation_image_ids": [str(NEW_ID)]}
    for split in ("train", "val", "test"):
        if set(LABELS) != {name for record in records if record["split"] == split for name in record["target_classes"]}:
            raise ValueError("Replacement loses class coverage in " + split)
    target.mkdir(parents=True)
    (target / "originals").mkdir()
    for record in records:
        origin = Path(image_path) if record["image_id"] == str(NEW_ID) else confined(source, record["file"])
        shutil.copy2(origin, target / record["file"])
        if hashlib.sha256((target / record["file"]).read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("Image changed during copy")
    (target / "instances_subset.json").write_bytes(annotation_bytes)
    shutil.copy2(metadata_path, target / "commons-imageinfo.json")
    with Image.open(image_path) as original:
        overlay = original.convert("RGB")
        draw = ImageDraw.Draw(overlay); x, y, width, height = BUS_BOX
        draw.rectangle((x, y, x+width, y+height), outline="red", width=16)
        overlay.thumbnail((1400, 1000)); overlay.save(target / "proposed-bus-bbox.jpg", quality=95)
    summary = publish_review(target, review, {"replaces_packet_sha256": old["packet_sha256"],
                                             "removed_image_id": REMOVED_ID, "manual_annotation_image_id": str(NEW_ID),
                                             "annotation_review": "pending_human"})
    with (target / "REVIEW.md").open("a", encoding="utf-8") as stream:
        stream.write("\n## Mudança concreta desta proposta\n\nA foto #004 de bonde (COCO514376) foi substituída por um ônibus real do Commons, autor Znns, CC-BY4.0. O IDlocal900000001 tem caixa proposta pelo agente, não anotação humana. Revise também `proposed-bus-bbox.jpg`. ID393226 passou de treino para teste para preservar semáforo no teste; nenhum treino foi executado antes desta mudança. Os originais do pacote anterior continuam preservados. O hash deste pacote também vincula o JSON completo de anotações; trocar uma caixa invalida a aprovação.\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True); parser.add_argument("--target", required=True)
    parser.add_argument("--image", required=True); parser.add_argument("--commons-metadata", required=True)
    args = parser.parse_args()
    print(json.dumps(replace(args.source, args.target, args.image, args.commons_metadata), indent=2))
