"""Explicit real-dataset training. Does not download data or publish children's images."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

def validate_names(names):
    from vision.service import LABELS
    expected = list(LABELS)
    if isinstance(names, dict):
        if any(type(k) is not int for k in names) or set(names) != set(range(len(expected))):
            raise ValueError("Class IDs must be integers 0..11")
        names = [names[i] for i in range(len(expected))]
    if not isinstance(names, list) or names != expected:
        raise ValueError("Class names must exactly match the 12 service classes in order")
    return names


def load_dataset_config(dataset):
    import yaml
    # Reject duplicate mapping keys instead of silently retaining the last value.
    class UniqueLoader(yaml.SafeLoader):
        pass
    def unique_mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError("Duplicate YAML mapping key")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result
    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
    data = Path(dataset).resolve()
    config = yaml.load(data.read_text(encoding="utf-8-sig"), Loader=UniqueLoader)
    if not isinstance(config, dict):
        raise ValueError("Dataset YAML must be a mapping")
    validate_names(config.get("names"))
    if "nc" in config and (type(config["nc"]) is not int or config["nc"] != 12):
        raise ValueError("nc must be 12")
    if any(not config.get(key) for key in ("train", "val", "test")):
        raise ValueError("Train, validation and test splits must be declared")
    return data, config


def validate_dataset(dataset, provenance):
    data, _ = load_dataset_config(dataset)
    metadata = json.loads(Path(provenance).read_text(encoding="utf-8-sig"))
    if not isinstance(metadata, dict) or metadata.get("real_images") is not True:
        raise ValueError("Document verified real-image provenance")
    for key in ("source_url", "license", "split_method"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError("Missing provenance: " + key)
    validate_names(metadata.get("class_names"))
    return data, metadata


def reserve_output(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    return path


def train(dataset, provenance, epochs=40, output=None, *, device="cpu", imgsz=320, batch=2, workers=0):
    if type(epochs) is not int or epochs < 1:
        raise ValueError("epochs must be a positive integer")
    if type(imgsz) is not int or imgsz < 32 or imgsz % 32:
        raise ValueError("imgsz must be a positive multiple of 32, minimum 32")
    if type(batch) is not int or batch < 1 or type(workers) is not int or workers < 0:
        raise ValueError("batch must be positive and workers nonnegative integers")
    if not isinstance(device, str) or not device.strip():
        raise ValueError("device must be cpu or an explicitly selected device")
    data, metadata = validate_dataset(dataset, provenance)
    from vision.audit import audit
    dataset_audit = audit(data, provenance)
    from ultralytics import YOLO
    root = Path(__file__).parent
    out = reserve_output(output or root/"artifacts")
    import yaml
    _, config = load_dataset_config(data)
    # Ultralytics resolves relative `path` against its datasets_dir, not our YAML.
    config["path"] = str((data.parent / config.get("path", ".")).resolve())
    resolved_data = out / "dataset-resolved.yaml"
    resolved_data.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    model = YOLO("yolo11n.pt")
    model.train(data=str(resolved_data), epochs=epochs, imgsz=imgsz, batch=batch, device=device,
                workers=workers, cache=False, seed=42, deterministic=True,
                project=str(root/"runs"), name=out.name, exist_ok=False)
    best = Path(model.trainer.best)
    evaluation = YOLO(str(best)).val(data=str(resolved_data), split="test", imgsz=imgsz,
                                    batch=batch, device=device, workers=workers,
                                    plots=True, save_json=True, project=str(root/"runs"),
                                    name=out.name + "-test", exist_ok=False)
    with best.open("rb") as source, (out/"best.pt").open("xb") as target:
        shutil.copyfileobj(source, target)
    per_class = {name: {"precision": float(evaluation.box.p[i]),
                        "recall": float(evaluation.box.r[i]),
                        "map50": float(evaluation.box.ap50[i]),
                        "map50_95": float(evaluation.box.ap[i])}
                 for i, class_id in enumerate(evaluation.box.ap_class_index)
                 for name in [metadata["class_names"][int(class_id)]]}
    metadata.update(trained_on_real_images=True, epochs=epochs, model="yolo11n",
                    device=device, imgsz=imgsz, batch=batch, workers=workers, seed=42,
                    inference={"conf": 0.5, "imgsz": imgsz},
                    quality_validated=False, dataset_audit=dataset_audit,
                    evaluation_directory=str(evaluation.save_dir), per_class_metrics=per_class,
                    dataset_yaml_sha256=hashlib.sha256(data.read_bytes()).hexdigest(),
                    checkpoint_sha256=hashlib.sha256((out/"best.pt").read_bytes()).hexdigest(),
                    test_metrics={str(k): float(v) for k,v in evaluation.results_dict.items()})
    with (out/"model_manifest.json").open("x", encoding="utf-8") as target:
        json.dump(metadata, target, indent=2)
    with (out/"error_analysis.md").open("x", encoding="utf-8") as target:
        target.write("# Revisão humana pendente\n\nNão há erros analisados automaticamente. "
                     "Use as predições e a matriz de confusão da pasta de avaliação indicada no manifesto. "
                     "Registre pelo menos cinco erros reais (se ocorrerem), com image_id, split=test, "
                     "classe esperada/predita, confiança, condição, hipótese e ação. "
                     "Não altere o treino com base no teste; novos ajustes exigem novo holdout.\n")
    return metadata

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--provenance",required=True)
    p.add_argument("--epochs", type=int, default=40)
    p.add_argument("--output", help="New artifact directory; existing directories are never reused")
    p.add_argument("--device", default="cpu")
    p.add_argument("--imgsz", type=int, default=320)
    p.add_argument("--batch", type=int, default=2)
    p.add_argument("--workers", type=int, default=0)
    a=p.parse_args()
    print(json.dumps(train(a.dataset,a.provenance,a.epochs,a.output,device=a.device,
                           imgsz=a.imgsz,batch=a.batch,workers=a.workers),indent=2))
