"""One Windows entry point for the local robot application and installed AI services."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.request
import webbrowser

from robot.voice import VoiceAssistant

OLLAMA = 'http://127.0.0.1:11434'


def request_json(url, *, data=None, timeout=3):
    request = urllib.request.Request(url, None if data is None else json.dumps(data).encode(),
                                     {} if data is None else {'Content-Type':'application/json'})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=timeout) as response:
        return json.load(response)


def port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=.5): return True
    except OSError: return False


def start_ollama():
    executable = shutil.which('ollama')
    if not executable:
        installed = Path(os.getenv('LOCALAPPDATA', '')) / 'Programs/Ollama/ollama.exe'
        if installed.is_file(): executable = str(installed)
    if not executable: raise RuntimeError('Ollama não instalado. Instale o Ollama e execute ollama pull qwen3:4b.')
    log = Path(tempfile.gettempdir()) / 'acolhe-ollama.log'
    print('Iniciando Ollama em segundo plano...', flush=True)
    with log.open('ab') as output:
        return subprocess.Popen([executable, 'serve'], stdin=subprocess.DEVNULL, stdout=output,
                                stderr=subprocess.STDOUT, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))


def ensure_ollama(model):
    try: tags = request_json(OLLAMA + '/api/tags')
    except (OSError, ValueError):
        if port_open('127.0.0.1', 11434):
            raise RuntimeError('A porta 11434 está ocupada, mas o Ollama não responde. Confira o serviço Ollama.')
        child = start_ollama()
        deadline = time.monotonic() + 30
        while True:
            try:
                tags = request_json(OLLAMA + '/api/tags', timeout=1)
                break
            except (OSError, ValueError):
                if child.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError('Ollama não iniciou. Consulte o arquivo acolhe-ollama.log na pasta temporária do Windows.')
                time.sleep(.5)
    if not isinstance(tags, dict) or not isinstance(tags.get('models'), list):
        raise RuntimeError('Ollama retornou uma lista de modelos inválida. Confira o serviço na porta 11434.')
    installed = {entry.get('name') for entry in tags['models'] if isinstance(entry, dict)}
    name = model if ':' in model else model + ':latest'
    if name not in installed:
        raise RuntimeError(f'Modelo ausente. Execute uma vez: ollama pull {model}')
    print(f'Carregando IA local ({model})...', flush=True)
    try:
        response = request_json(OLLAMA + '/api/generate', data={
            'model':model, 'prompt':'', 'stream':False, 'keep_alive':'10m',
            'options':{'num_ctx':4096}}, timeout=90)
        if not isinstance(response, dict) or response.get('done') is not True or response.get('error'): raise ValueError('Carga incompleta')
    except (OSError, ValueError) as exc:
        raise RuntimeError(f'Não foi possível carregar {model}. Confira memória disponível e o serviço Ollama.') from exc


def prepare_services():
    missing = [name for name in ('serial', 'numpy', 'faster_whisper') if importlib.util.find_spec(name) is None]
    if missing: raise RuntimeError('Dependências ausentes: ' + ', '.join(missing) + '. Execute Preparar-Robo.cmd.')
    voice = VoiceAssistant()
    status = voice.status()
    if not status['whisper_files'] or not status['piper_files']:
        raise RuntimeError('Arquivos Whisper/Piper ausentes. Execute Preparar-Robo.cmd com a pasta dos modelos.')
    ensure_ollama(voice.model)
    # Validate the installed runtime without recording or playing user audio.
    print('Verificando voz Piper...', flush=True)
    voice._speak('Acolhe pronto.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verificar serviços sem abrir navegador ou servidor.')
    args = parser.parse_args()
    try:
        prepare_services()
        if args.check:
            print('IA e voz disponíveis. Nenhum motor foi acionado.', flush=True)
            return 0
        host, port = os.getenv('HOST', '127.0.0.1'), int(os.getenv('PORT', '8080'))
        local_host = '127.0.0.1' if host == '0.0.0.0' else host
        url = f'http://{local_host}:{port}'
        if port_open(local_host, port):
            try:
                health = request_json(url + '/api/health')
                status = request_json(url + '/api/robot/status')
                if not isinstance(health, dict) or not isinstance(status, dict) or health.get('mode') != 'academic_demo' or not isinstance(status.get('voice'), dict):
                    raise ValueError('Outro serviço')
            except (OSError, ValueError) as exc:
                raise RuntimeError(f'Porta {port} ocupada por um serviço indisponível ou diferente do Acolhe.') from exc
            print('O Acolhe já está aberto. Reutilizando o servidor e a conexão do robô.', flush=True)
            webbrowser.open(url + '/robo.html')
            return 0
        from app.server import create_server
        server = create_server(host, port)
        print(f'Acolhe pronto: {url}/robo.html\nMantenha esta janela aberta. Ctrl+C encerra o Acolhe.', flush=True)
        browser = threading.Timer(.5, webbrowser.open, args=[url + '/robo.html'])
        browser.daemon = True
        browser.start()
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally:
            browser.cancel()
            server.server_close()
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'Não foi possível iniciar o Acolhe: {exc}', flush=True)
        return 1


if __name__ == '__main__': raise SystemExit(main())
