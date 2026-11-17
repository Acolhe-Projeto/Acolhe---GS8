"""Copy only local voice assets; never import the Talos application."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent.parent / 'maker-lab' / 'cp5' / 'TalosAI_assistant')
    args = parser.parse_args()
    destination = ROOT / 'robot' / '.models'
    source = args.source
    whisper = source / 'modelos' / 'whisper-small'
    piper = source / 'piper'
    required = [whisper / name for name in ('model.bin', 'config.json', 'tokenizer.json', 'vocabulary.txt')]
    required += [piper / name for name in ('piper.exe', 'pt_BR-faber-medium.onnx', 'pt_BR-faber-medium.onnx.json',
                                          'espeak-ng.dll', 'onnxruntime.dll', 'piper_phonemize.dll')]
    missing = [str(path.relative_to(source)) for path in required if not path.is_file()]
    if not (piper / 'espeak-ng-data').is_dir() or not any((piper / 'espeak-ng-data').rglob('*')):
        missing.append('piper/espeak-ng-data/ (com os dados do runtime)')
    if missing:
        parser.error('Pacote local incompleto. Use --source com modelos/whisper-small e piper/. Faltam: ' + ', '.join(missing))
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(whisper, destination / 'whisper-small', dirs_exist_ok=True)
    # The Windows Piper runtime needs its DLLs and espeak phoneme data.
    target = destination / 'piper'
    target.mkdir(exist_ok=True)
    for path in piper.iterdir():
        if path.is_file() and (path.name == 'piper.exe' or path.suffix == '.dll' or path.name.startswith('pt_BR-faber-medium.onnx')):
            shutil.copy2(path, target / path.name)
        elif path.is_dir() and path.name == 'espeak-ng-data':
            shutil.copytree(path, target / path.name, dirs_exist_ok=True)
    print('Modelos de voz copiados para robot/.models. Nenhum código do Talos foi importado.')
    print('Qwen3 4B requer Ollama local com o modelo qwen3:4b disponível.')


if __name__ == '__main__': main()
