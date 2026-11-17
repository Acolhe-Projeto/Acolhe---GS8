"""Real local model checks with synthetic phrases, never a hardware claim."""
import base64
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import time
import wave

from robot.voice import VoiceAssistant


def main():
    import numpy as np
    assistant = VoiceAssistant()
    cases = [
        ('Olá, qual é o seu nome?', {'valid': False}),
        ('Como atravessar a rua com segurança?', {'valid': False}),
        ('Como está a temperatura da sala?', {'valid': True, 'temperature': 26, 'humidity': 52}),
        ('Como está a umidade?', {'valid': False}),
        ('Qual é a cotação da bolsa hoje?', {'valid': False}),
    ]
    results = []
    for question, sensor_fixture in cases:
        started = time.monotonic()
        result = {'input': question, 'sensor_fixture': sensor_fixture, 'physical_verified': False}
        try:
            synthesized = base64.b64decode(assistant._speak(question))
            with wave.open(BytesIO(synthesized), 'rb') as wav:
                rate, pcm = wav.getframerate(), wav.readframes(wav.getnframes())
            samples = np.frombuffer(pcm, dtype='<i2').astype(np.float32)
            count = int(len(samples) * 16000 / rate)
            resampled = np.interp(np.arange(count) * rate / 16000, np.arange(len(samples)), samples).astype('<i2').tobytes()
            interaction = assistant.chat({'pcm16': base64.b64encode(resampled).decode()}, sensor_fixture)
            audio = base64.b64decode(interaction.pop('audio_wav') or '')
            with wave.open(BytesIO(audio), 'rb') as wav:
                interaction['output_audio_seconds'] = round(wav.getnframes() / wav.getframerate(), 2)
            interaction['output_wav_bytes'] = len(audio)
            result.update(interaction)
            result['passed'] = bool(interaction['transcript'] and interaction['answer'] and not interaction['errors'] and len(audio) > 44)
            result['semantic_review'] = 'pending_human_review'
        except Exception as exc:
            result.update(passed=False, error=str(exc), component=getattr(exc, 'component', 'test'))
        result['total_seconds'] = round(time.monotonic() - started, 2)
        results.append(result)
        print(json.dumps(result, ensure_ascii=True), flush=True)
    evidence = {'kind': 'synthetic_audio_real_local_models', 'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'physical_verified': False,
                'microphone_tested': False, 'audible_playback_verified': False,
                'sensor_source': 'explicit test fixtures, not physical DHT11',
                'model': assistant.model, 'semantic_review': 'pending_human_review',
                'latency_target_seconds': 10, 'latency_target_met_in_all_cases': all(r.get('elapsed_seconds', 999) <= 10 for r in results),
                'source_sha256': {name: hashlib.sha256((Path(__file__).resolve().parent / name).read_bytes()).hexdigest() for name in ('voice.py', 'hardware.py')},
                'results': results}
    path = Path(__file__).resolve().parent.parent / 'docs' / 'evidencias' / 'maker-modelos-locais.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    if not all(r['passed'] for r in results): raise SystemExit(1)


if __name__ == '__main__': main()
