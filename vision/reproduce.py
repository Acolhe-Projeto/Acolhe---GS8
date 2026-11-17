"""Rebuild the exact reviewed pilot from public URLs; never downloads model weights."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from urllib.parse import urlparse
import urllib.request

ROOT = Path(__file__).resolve().parent


def download(url, target, expected):
    parsed = urlparse(url)
    allowed = (parsed.hostname in {'images.cocodataset.org', 'upload.wikimedia.org'} or
               parsed.hostname == 's3.amazonaws.com' and parsed.path.startswith('/images.cocodataset.org/'))
    if parsed.scheme != 'https' or not allowed:
        raise ValueError('Only the recorded HTTPS COCO/Commons image sources are allowed')
    request = urllib.request.Request(url, headers={'User-Agent': 'AcolheGS/1.0 educational dataset reproduction'})
    with urllib.request.urlopen(request, timeout=40) as response:
        image = response.read(20*1024*1024+1)
    if len(image) > 20*1024*1024 or hashlib.sha256(image).hexdigest() != expected:
        raise ValueError('Image differs from reviewed bytes; do not replace the recorded hash')
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(image)


def reproduce(output, cache=None):
    from vision.audit import audit, confined
    bundle = json.loads((ROOT/'reports/reproduction.json').read_text(encoding='utf-8'))
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    # An interrupted run leaves a partial new directory for inspection, never overwrites it.
    for record in bundle['images']:
        target = confined(output, record['file'])
        if cache is not None:
            cached = confined(Path(cache).resolve(), record['file'])
            if hashlib.sha256(cached.read_bytes()).hexdigest() != record['sha256']:
                raise ValueError('Local cache differs from reviewed image')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cached, target)
        else:
            download(record['download_url'], target, record['sha256'])
        label = confined(output, record['label_file'])
        label.parent.mkdir(parents=True, exist_ok=True)
        label.write_bytes(record['label_text'].encode('utf-8'))
    (output/'dataset.yaml').write_bytes(bundle['dataset_yaml'].encode('utf-8'))
    (output/'provenance.json').write_text(json.dumps(bundle['provenance'], ensure_ascii=False, indent=2), encoding='utf-8')
    result = audit(output/'dataset.yaml', output/'provenance.json')
    if result['dataset_fingerprint_sha256'] != bundle['dataset_fingerprint_sha256']:
        raise ValueError('Reproduced dataset fingerprint mismatch')
    (output/'audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New directory; existing folders are refused')
    parser.add_argument('--cache', type=Path, help='Existing curated dataset for offline reconstruction, still hash-verified')
    args = parser.parse_args()
    print(json.dumps(reproduce(args.output, args.cache), indent=2))
