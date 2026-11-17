"""Prepare a small COCO review packet. Approval is explicit and bound to image hashes."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import random
import re
import textwrap
import urllib.request
import urllib.error
import zipfile

from vision.service import LABELS
from vision.audit import confined

ANNOTATIONS = "https://fast-ai-coco.s3.amazonaws.com/annotations_trainval2017.zip"
LICENSE = "https://creativecommons.org/licenses/by/2.0/"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Acolhe-academic-dataset-review/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read(), response.geturl()


class RemoteZip(io.RawIOBase):
    """Read one ZIP member with verified HTTPS ranges, rather than downloading all COCO."""
    def __init__(self, url):
        self.url, self.position = url, 0
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as response:
            self.length = int(response.headers["Content-Length"])

    def seekable(self): return True
    def tell(self): return self.position
    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else self.length + offset
        return self.position
    def read(self, size=-1):
        size = self.length - self.position if size < 0 else min(size, self.length - self.position)
        if size <= 0: return b""
        request = urllib.request.Request(self.url, headers={"Range": f"bytes={self.position}-{self.position+size-1}"})
        with urllib.request.urlopen(request, timeout=90) as response:
            if response.status != 206: raise RuntimeError("Remote ZIP server ignored the requested byte range")
            data = response.read()
        self.position += len(data)
        return data


def metadata(root, name):
    target = root / name
    if not target.exists():
        with zipfile.ZipFile(RemoteZip(ANNOTATIONS)) as archive:
            target.write_bytes(archive.read("annotations/" + name))
    return json.loads(target.read_text(encoding="utf-8"))


def flickr_credit(html):
    for raw in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        try: structured = json.loads(raw)
        except ValueError: continue
        for item in structured.get("@graph", [structured]):
            if item.get("@type") == "ImageObject" and item.get("license", "").replace("http:", "https:") == LICENSE:
                author = item.get("author", {})
                if author.get("name") and author.get("url"):
                    return {"author": author["name"], "author_url": author["url"], "license": LICENSE}
    raise ValueError("Current source page does not confirm CC-BY 2.0 and author")


def fingerprint(records):
    fields = [{key: record[key] for key in ("image_id", "file", "sha256", "split", "source_url", "author", "license", "annotations_sha256") if key in record}
              for record in records]
    return hashlib.sha256(json.dumps(fields, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def build(root, train=4, val=1, test=1, excluded=(), cached_only=False, source_split="val2017", minimum_train_images=0, minimum_val_images=0):
    from PIL import Image, ImageDraw, ImageFont
    if (any(type(n) is not int or n < 1 for n in (train, val)) or type(test) is not int or test < 0
            or any(type(n) is not int or n < 0 for n in (minimum_train_images, minimum_val_images))
            or source_split not in ("train2017", "val2017")):
        raise ValueError("Train/validation need positive per-class counts; test may be zero; source must be COCO2017")
    root = Path(root).resolve()
    if (root / "reviews.json").exists(): raise FileExistsError("Choose a fresh review directory")
    root.mkdir(parents=True, exist_ok=True)
    coco = metadata(root, "instances_" + source_split + ".json")
    captions = metadata(root, "captions_" + source_split + ".json")
    texts = defaultdict(list)
    for caption in captions["annotations"]: texts[caption["image_id"]].append(caption["caption"])
    annotations = defaultdict(list)
    categories = {item["id"]: item["name"] for item in coco["categories"]}
    for item in coco["annotations"]: annotations[item["image_id"]].append(item)
    candidates = []
    for image in coco["images"]:
        if not re.fullmatch(r"\d{12}\.jpg", image["file_name"]): continue
        boxes = [item for item in annotations[image["id"]] if categories[item["category_id"]] in LABELS]
        people = sum(categories[item["category_id"]] == "person" for item in annotations[image["id"]])
        description = " ".join(texts[image["id"]]).casefold()
        if image["id"] in excluded or image["license"] != 4 or not boxes or any(item.get("iscrowd") for item in boxes): continue
        if re.search(r"\b(child|children|kid|kids|boy|girl|baby|babies|toddler|teenager)\b", description): continue
        if people and not re.search(r"\b(man|woman|men|women|adult)\b", description): continue
        if any((x := item["bbox"])[0] < 0 or x[1] < 0 or x[2] <= 0 or x[3] <= 0 or
               x[0]+x[2] > image["width"] or x[1]+x[3] > image["height"] for item in boxes): continue
        candidates.append({**image, "target_classes": sorted({categories[item["category_id"]] for item in boxes}),
                           "person_annotations": people})
    random.Random(42).shuffle(candidates)
    candidates.sort(key=lambda image: image["person_annotations"] != 0)
    selected, failures, used = [], [], set()
    photos = root / "originals"; photos.mkdir(exist_ok=True)
    credit_cache = root / "source-records"; credit_cache.mkdir(exist_ok=True)
    if cached_only:
        candidates = [image for image in candidates if (credit_cache / (str(image["id"]) + ".json")).is_file()]

    def acquire(image):
        cached = credit_cache / (str(image["id"]) + ".json")
        path = photos / image["file_name"]
        if cached.is_file() and path.is_file():
            record = json.loads(cached.read_text(encoding="utf-8"))
            if hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]:
                return record
        if cached_only:
            raise ValueError("Verified cache missing or changed; offline mode will not fetch replacements")
        flickr_id = re.search(r"/(\d+)_", image["flickr_url"]).group(1)
        page, source_url = fetch("https://www.flickr.com/photo.gne?id=" + flickr_id)
        credit = flickr_credit(page.decode("utf-8"))
        image_url = "https://s3.amazonaws.com/images.cocodataset.org/" + source_split + "/" + image["file_name"]
        pixels = path.read_bytes() if path.is_file() else fetch(image_url)[0]
        with Image.open(io.BytesIO(pixels)) as picture:
            if picture.size != (image["width"], image["height"]): raise ValueError("Source dimensions changed")
            picture.verify()
        path.write_bytes(pixels)
        record = {"image_id": str(image["id"]), "file": "originals/" + image["file_name"],
                "source_url": source_url, "download_url": image_url, **credit,
                "sha256": hashlib.sha256(pixels).hexdigest(), "source_page_sha256": hashlib.sha256(page).hexdigest(),
                "source_checked_at": datetime.now(timezone.utc).isoformat(),
                "license_verification": "Current Flickr ImageObject declares CC-BY 2.0; human legal review pending",
                "privacy_reviewed": False, "reviewed_at": "", "target_classes": image["target_classes"],
                "person_annotations": image["person_annotations"], "captions": texts[image["id"]]}
        cached.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record

    for split, minimum in (("test", test), ("val", val), ("train", train)):
        if minimum == 0:
            continue
        counts = Counter()
        split_count = 0
        image_floor = {"train": minimum_train_images, "val": minimum_val_images}.get(split, 0)
        while min((counts[name] for name in LABELS), default=0) < minimum or split_count < image_floor:
            missing = {name for name in LABELS if counts[name] < minimum}
            if not missing: missing = set(LABELS)
            available = [image for image in candidates if image["id"] not in used and missing.intersection(image["target_classes"])]
            if not available: raise ValueError("Not enough verified candidates: " + str(missing))
            # Prefer photographs without annotated people, then cover multiple missing classes.
            available.sort(key=lambda image: (image["person_annotations"] != 0, -len(missing.intersection(image["target_classes"]))))
            batch = available[:4]
            with ThreadPoolExecutor(max_workers=4) as workers:
                futures = [(image, workers.submit(acquire, image)) for image in batch]
                for image, future in futures:
                    try: record = future.result()
                    except Exception as exc:
                        used.add(image["id"])
                        failures.append({"image_id": str(image["id"]), "error": type(exc).__name__ + ": " + str(exc)})
                        if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                            raise RuntimeError("Flickr rate limit reached; stop and use verified cache or wait for Retry-After") from exc
                        continue
                    if not missing.intersection(record["target_classes"]): continue
                    used.add(image["id"])
                    selected.append(dict(record, split=split, review_number=len(selected)+1))
                    split_count += 1
                    counts.update(record["target_classes"])
                    missing = {name for name in LABELS if counts[name] < minimum}
                    if not missing and split_count < image_floor: missing = set(LABELS)
            print(split, len(selected), dict(counts), flush=True)
            (root / "selection-progress.json").write_text(json.dumps({"images": selected, "failures": failures}, ensure_ascii=False, indent=2), encoding="utf-8")
    if cached_only:
        for image in candidates:
            if image["id"] not in used:
                selected.append(dict(acquire(image), split="train", review_number=len(selected)+1))
    selected_ids = {int(r["image_id"]) for r in selected}
    subset = {"images": [im for im in coco["images"] if im["id"] in selected_ids],
              "categories": coco["categories"], "annotations": [a for a in coco["annotations"] if a["image_id"] in selected_ids]}
    annotation_path = root / "instances_subset.json"
    annotation_path.write_text(json.dumps(subset, ensure_ascii=False), encoding="utf-8")
    annotation_hash = hashlib.sha256(annotation_path.read_bytes()).hexdigest()
    for record in selected: record["annotations_sha256"] = annotation_hash
    packet_hash = fingerprint(selected)
    review = {"source_url": "https://cocodataset.org/", "license": "Per-image CC-BY 2.0 confirmed on Flickr; annotations CC-BY 4.0",
              "real_images": True, "split_method": "COCO " + source_split + " subset; deterministic seed42; images split before any augmentation",
              "annotations_file": annotation_path.name, "annotations_sha256": annotation_hash,
              "class_names": list(LABELS), "packet_sha256": packet_hash, "human_approval": "pending", "images": selected}
    (root / "reviews.json").write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
    (root / "download_failures.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")
    return publish_review(root, review, {"cached_only": cached_only, "requested_minimum_per_class": {"train": train, "val": val, "test": test}})


def publish_review(root, review, extra_summary=None):
    from PIL import Image, ImageDraw, ImageFont
    selected = review["images"]
    packet_hash = review["packet_sha256"]
    (root / "reviews.json").write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
    sheets = []
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    for start in range(0, len(selected), 12):
        sheet = Image.new("RGB", (1200, 1200), "white"); draw = ImageDraw.Draw(sheet)
        for offset, record in enumerate(selected[start:start+12]):
            x, y = (offset % 4)*300, (offset//4)*400
            with Image.open(root / record["file"]) as source:
                source.thumbnail((290, 260)); sheet.paste(source, (x+(290-source.width)//2, y))
            lines = [f"#{record['review_number']:03d} ID {record['image_id']} [{record['split']}]",
                     *textwrap.wrap(", ".join(record["target_classes"]), width=36),
                     record["author"][:32], "CC-BY " + ("4.0" if "/4.0" in record["license"] else "2.0") + " | HUMAN REVIEW PENDING"]
            for line_no, line in enumerate(lines): draw.text((x+5, y+265+line_no*19), line[:38], font=font, fill="black")
        path = root / f"contact-{start//12+1:02d}.jpg"; sheet.save(path, quality=90); sheets.append(path.name)
    summary = {"images": len(selected), "image_bytes": sum((root/r["file"]).stat().st_size for r in selected),
               "packet_sha256": packet_hash, "contact_sheets": sheets,
               "split_images": dict(Counter(r["split"] for r in selected)),
               "class_images_per_split": {s: dict(Counter(c for r in selected if r["split"] == s for c in r["target_classes"])) for s in ("train", "val", "test")},
               "human_approval": "pending", "privacy_reviewed_true": 0}
    summary.update(extra_summary or {})
    (root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    columns = ["review_number", "image_id", "split", "file", "target_classes", "person_annotations", "author", "author_url", "source_url", "license", "sha256", "privacy_reviewed"]
    with (root / "inventory.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns); writer.writeheader()
        for record in selected:
            writer.writerow({key: "; ".join(record[key]) if key == "target_classes" else record[key] for key in columns})
    (root / "REVIEW.md").write_text(
        "# Pacote de imagens para revisão humana\n\n"
        + f"{len(selected)} fotografias selecionadas. Hash do pacote: `{packet_hash}`.\n\n"
        + "Revise somente as imagens numeradas nas folhas abaixo; arquivos adicionais em originals/ são cache de candidatas descartadas e não pertencem ao pacote. Confira ausência de crianças identificáveis/dados sensíveis, adequação dos objetos, autoria e licença. Captions e anotações não garantem privacidade.\n\n"
        + "\n".join(f"![Folha {i+1}]({name})" for i, name in enumerate(sheets))
        + "\n\nCréditos individuais e URLs estão em inventory.csv e reviews.json. As fontes e licenças de cada foto estão registradas no inventário; a revisão jurídica/humana permanece pendente. Nenhum campo privacy_reviewed foi aprovado pelo agente.\n\n"
        + "Depois da aprovação explícita deste conjunto exato, registrar o nome do revisor e a referência à autorização com:\n\n"
        + f'`python -m vision.public_review approve --root "{root.as_posix()}" --packet-sha256 {packet_hash} --reviewer "NOME DO REVISOR" --reference "REFERENCIA DA APROVACAO"`\n\n'
        + "O comando recusa hashes/imagens alterados e nunca sobrescreve uma aprovação anterior. Sem aprovação, prepare/audit/train continuam bloqueados. Os splits são anteriores às transformações; o pacote é um piloto pequeno, não prova de generalização.\n",
        encoding="utf-8")
    return summary


def approve(root, expected_hash, reviewer, reference):
    root = Path(root).resolve()
    path = root / "reviews.json"
    review = json.loads(path.read_text(encoding="utf-8"))
    if not reviewer.strip() or not reference.strip(): raise ValueError("Human reviewer and explicit approval reference required")
    if expected_hash != review["packet_sha256"] or fingerprint(review["images"]) != expected_hash:
        raise ValueError("Review packet changed after approval")
    for record in review["images"]:
        if hashlib.sha256(confined(root, record["file"]).read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("An image changed after review")
    if review.get("annotations_sha256"):
        expected_annotations = review["annotations_sha256"]
        annotation_file = confined(root, review["annotations_file"])
        if hashlib.sha256(annotation_file.read_bytes()).hexdigest() != expected_annotations or any(record.get("annotations_sha256") != expected_annotations for record in review["images"]):
            raise ValueError("Annotations changed after the review packet was prepared")
    now = datetime.now(timezone.utc).isoformat()
    for record in review["images"]:
        record.update(privacy_reviewed=True, reviewed_at=now, reviewer=reviewer, approval_reference=reference)
    review.update(human_approval="approved", approved_packet_sha256=expected_hash)
    target = root / "reviews.approved.json"
    with target.open("x", encoding="utf-8") as stream: json.dump(review, stream, indent=2, ensure_ascii=False)
    return str(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("build"); make.add_argument("--root", required=True)
    make.add_argument("--train", type=int, default=4); make.add_argument("--val", type=int, default=1); make.add_argument("--test", type=int, default=1)
    make.add_argument("--source-split", choices=("train2017", "val2017"), default="val2017")
    make.add_argument("--minimum-train-images", type=int, default=0)
    make.add_argument("--minimum-val-images", type=int, default=0)
    make.add_argument("--exclude", type=int, nargs="*", default=[])
    make.add_argument("--cached-only", action="store_true", help="Use previously verified source records only; reserve all remaining images for training")
    approval = sub.add_parser("approve"); approval.add_argument("--root", required=True)
    approval.add_argument("--packet-sha256", required=True); approval.add_argument("--reviewer", required=True); approval.add_argument("--reference", required=True)
    args = parser.parse_args()
    result = build(args.root, args.train, args.val, args.test, args.exclude, args.cached_only, args.source_split, args.minimum_train_images, args.minimum_val_images) if args.command == "build" else approve(args.root,args.packet_sha256,args.reviewer,args.reference)
    print(json.dumps(result, indent=2, ensure_ascii=False))
