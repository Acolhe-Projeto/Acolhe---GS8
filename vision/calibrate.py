"""Select confidence on validation only; report fixed-threshold detection counts."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def iou(a, b):
    intersection = max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))
    union = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - intersection
    return intersection / union if union > 0 else 0.0


def score(images, confidence):
    counts = [[0, 0, 0] for _ in range(12)]  # TP, FP, FN
    for image in images:
        remaining = set(range(len(image['gold'])))
        for prediction in sorted(image['predictions'], key=lambda p: -p['confidence']):
            if prediction['confidence'] < confidence:
                continue
            cls = prediction['class_id']
            candidates = [i for i in remaining if image['gold'][i]['class_id'] == cls]
            best = max(candidates, key=lambda i: iou(prediction['xyxy'], image['gold'][i]['xyxy']), default=None)
            if best is not None and iou(prediction['xyxy'], image['gold'][best]['xyxy']) >= 0.5:
                counts[cls][0] += 1
                remaining.remove(best)
            else:
                counts[cls][1] += 1
        for i in remaining:
            counts[image['gold'][i]['class_id']][2] += 1
    def metrics(row):
        tp, fp, fn = row
        return dict(tp=tp, fp=fp, fn=fn, precision=tp/(tp+fp) if tp+fp else 0,
                    recall=tp/(tp+fn) if tp+fn else 0, f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return dict(confidence=confidence, iou=0.5,
                **metrics([sum(row[i] for row in counts) for i in range(3)]),
                per_class=[metrics(row) for row in counts])


def collect(model, root, config, split, imgsz):
    from PIL import Image
    from vision.audit import confined, IMAGE_SUFFIXES
    images = []
    folder = confined(root, config[split])
    for path in sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES):
        with Image.open(path) as photo:
            width, height = photo.size
        label = folder.parent.parent / 'labels' / folder.name / (path.stem + '.txt')
        gold = []
        for line in label.read_text().splitlines():
            cls, x, y, w, h = map(float, line.split())
            gold.append({'class_id': int(cls), 'xyxy': [(x-w/2)*width, (y-h/2)*height, (x+w/2)*width, (y+h/2)*height]})
        predictions = []
        for result in model.predict(str(path), device='cpu', imgsz=imgsz, conf=0.001, save=False, verbose=False):
            for box in result.boxes:
                predictions.append({'class_id': int(box.cls.item()), 'confidence': float(box.conf.item()), 'xyxy': box.xyxy[0].tolist()})
        images.append({'file': path.relative_to(root).as_posix(), 'gold': gold, 'predictions': predictions})
    return images


def calibrate(artifacts, dataset, provenance, output, evaluate_test=False):
    from vision.audit import audit
    from vision.train import load_dataset_config
    from ultralytics import YOLO
    if Path(output).exists():
        raise FileExistsError(output)
    checked = audit(dataset, provenance)
    data, config = load_dataset_config(dataset)
    root = (data.parent / config.get('path', '.')).resolve()
    artifacts = Path(artifacts)
    manifest = json.loads((artifacts/'model_manifest.json').read_text())
    checkpoint = artifacts/'best.pt'
    digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    if digest != manifest['checkpoint_sha256']:
        raise ValueError('Checkpoint hash mismatch')
    model = YOLO(str(checkpoint))
    validation = collect(model, root, config, 'val', manifest['imgsz'])
    grid = [score(validation, c) for c in [0.05, 0.10, 0.15, 0.20, 0.25, 0.35, 0.50, 0.65, 0.80]]
    chosen = max(grid, key=lambda r: (r['f1'], r['precision'], r['confidence']))
    report = {'selection_rule': 'Maximum micro F1 on validation; ties precision then higher confidence. IoU0.5, one-to-one same-class matching.',
              'checkpoint_sha256': digest, 'dataset_fingerprint_sha256': checked['dataset_fingerprint_sha256'],
              'imgsz': manifest['imgsz'], 'class_names': manifest['class_names'], 'validation_images': len(validation),
              'validation_grid': grid, 'selected': chosen, 'quality_validated': False}
    if evaluate_test:
        test = collect(model, root, config, 'test', manifest['imgsz'])
        report.update(test_images=len(test), test=score(test, chosen['confidence']))
    with Path(output).open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
    return report


def activate(artifacts, report):
    from vision.service import inference_options
    path = Path(artifacts) / 'model_manifest.json'
    manifest = json.loads(path.read_text())
    digest = hashlib.sha256((Path(artifacts)/'best.pt').read_bytes()).hexdigest()
    if digest != report['checkpoint_sha256'] or digest != manifest['checkpoint_sha256']:
        raise ValueError('Calibration belongs to a different checkpoint')
    manifest['inference'] = inference_options({'inference': {'conf': report['selected']['confidence'], 'imgsz': report['imgsz']}})
    manifest['calibration'] = {'selected_on': 'validation_only', 'selection': report['selection_rule']}
    pending = path.with_suffix('.calibrating.json')
    with pending.open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, indent=2)
    os.replace(pending, path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', required=True)
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--provenance', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--evaluate-test', action='store_true', help='Only after validation selection is frozen')
    parser.add_argument('--activate', action='store_true', help='Apply the validation-selected confidence/image size to this artifact manifest')
    args = parser.parse_args()
    result = calibrate(args.artifacts, args.dataset, args.provenance, args.output, args.evaluate_test)
    if args.activate:
        activate(args.artifacts, result)
    print(json.dumps({k: result[k] for k in ('selected', 'test') if k in result}, indent=2))
