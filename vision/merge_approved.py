"""Union approved training/validation without changing split membership or test pixels."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from vision.audit import audit


def merge(sources, heldout, output):
    sources = [Path(p).resolve() for p in sources]
    heldout, output = Path(heldout).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    inventories, source_audits = {}, []
    for root in dict.fromkeys([*sources, heldout]):
        checked = audit(root/'dataset.yaml', root/'provenance.json')
        inventories[root] = json.loads((root/'provenance.json').read_text(encoding='utf-8'))
        source_audits.append({'dataset': root.name, 'fingerprint': checked['dataset_fingerprint_sha256']})
    selected, ids, pixels = [], {}, {}
    for split in ('train', 'val', 'test'):
        for root in ([heldout] if split == 'test' else sources):
            for record in inventories[root]['images']:
                if record['split'] != split:
                    continue
                image_id, digest = record['image_id'], record['sha256']
                label = Path(record['file'].replace('images/', 'labels/')).with_suffix('.txt')
                label_bytes = (root/label).read_bytes()
                identity = (split, digest, hashlib.sha256(label_bytes).hexdigest())
                if image_id in ids:
                    if ids[image_id] != identity:
                        raise ValueError('Conflicting image ID, split, pixels or annotations')
                    continue
                if digest in pixels:
                    raise ValueError('Same pixels under different image IDs or splits')
                ids[image_id], pixels[digest] = identity, split
                selected.append((root, record, label_bytes))
    # All conflicts are rejected before creating the new destination.
    output.mkdir(parents=True)
    records = []
    for i, (root, record, label_bytes) in enumerate(selected):
        relative = Path('images')/record['split']/(f'image_{i:07d}'+Path(record['file']).suffix)
        target = output/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root/record['file'], target)
        label = output/Path(relative.as_posix().replace('images/', 'labels/')).with_suffix('.txt')
        label.parent.mkdir(parents=True, exist_ok=True)
        label.write_bytes(label_bytes)
        records.append({**record, 'file': relative.as_posix(), 'source_curated_dataset': root.name})
    (output/'dataset.yaml').write_bytes((heldout/'dataset.yaml').read_bytes())
    meta = {**inventories[heldout], 'images': records, 'source_audits': source_audits,
            'split_method': 'Union of approved train/val preserving membership; test exclusively from fixed heldout. Duplicate identical IDs merged, conflicting labels/splits rejected.',
            'human_approval': 'Composition of individually approved source records; no new blanket approval fabricated.'}
    meta['source_approvals'] = [
        {'dataset': root.name,
         'source_provenance_sha256': hashlib.sha256((root/'provenance.json').read_bytes()).hexdigest(),
         'declared_packet_hashes': sorted(set(inventories[root].get('approved_source_packets', []) +
             ([inventories[root]['approved_packet_sha256']] if inventories[root].get('approved_packet_sha256') else [])))}
        for root in dict.fromkeys([*sources, heldout])]
    for key in ('annotations_sha256', 'annotations_file', 'packet_sha256', 'approved_packet_sha256', 'approved_source_packets'):
        meta.pop(key, None)
    (output/'provenance.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    checked = audit(output/'dataset.yaml', output/'provenance.json')
    (output/'audit.json').write_text(json.dumps(checked, indent=2), encoding='utf-8')
    return checked


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', nargs='+', required=True)
    parser.add_argument('--heldout', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(merge(args.sources, args.heldout, args.output), indent=2))
