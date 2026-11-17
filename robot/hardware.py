"""One physical Uno connection. ACKs describe firmware, never observed movement."""
import json
import math
import threading
import time

VERSION = 'ACOLHE_V2'


class Telemetry:
    def __init__(self):
        self.temperature = self.humidity = self.received = None

    def update(self, sample, now):
        t, h = sample.get('temperature'), sample.get('humidity')
        valid = sample.get('valid') is True and all(type(x) in (int, float) and math.isfinite(x) for x in (t, h))
        valid = valid and 0 <= t <= 50 and 0 <= h <= 100
        self.temperature, self.humidity = (t, h) if valid else (None, None)
        self.received = now if valid else None
        return bool(valid)

    def snapshot(self, now):
        valid = self.received is not None and 0 <= now - self.received <= 6
        return {'sensor': 'DHT11', 'valid': valid,
                'temperature': self.temperature if valid else None,
                'humidity': self.humidity if valid else None,
                'age_seconds': round(now - self.received, 1) if self.received is not None else None}


class HeatActivity:
    def __init__(self):
        self.count = 0
        self.armed = True
        self.last = -float('inf')

    def update(self, temperature, now):
        if temperature is None:
            self.count = 0
            return False
        if temperature < 28:
            self.armed = True
        self.count = self.count + 1 if temperature >= 30 else 0
        if self.armed and self.count >= 3 and now - self.last >= 120:
            self.armed = False
            self.last = now
            return True
        return False


class RobotConnection:
    def __init__(self):
        self.lock = threading.RLock()
        self.lifecycle = threading.Lock()
        self.serial = None
        self.thread = None
        self.end = threading.Event()
        self.sensor = Telemetry()
        self.heat = HeatActivity()
        self.port = None
        self.error = None
        self.lcd_ok = None
        self.lcd_enabled = None
        self.board = None
        self.motor_control = None
        self.calibrations = {}
        self.pending = {}
        self.tested = {}
        self.last_gesture = -float('inf')
        self.last_message = None
        self.activity_id = 0
        self.activity = None
        self.ack = None

    @staticmethod
    def ports():
        try:
            from serial.tools import list_ports
            return [{'device': p.device, 'description': p.description} for p in list_ports.comports()]
        except ImportError:
            return []

    def connect(self, port):
        if not isinstance(port, str) or port not in [p['device'] for p in self.ports()]:
            raise ValueError('Escolha uma porta serial disponível na lista.')
        with self.lifecycle:
            self._close()
            try:
                import serial
                stream = serial.Serial(port, 115200, timeout=.1, write_timeout=.3)
                started = time.monotonic()
                deadline = started + 6
                next_hello = started
                recovered = False
                hello = None
                while time.monotonic() < deadline:
                    now = time.monotonic()
                    if now >= next_hello:
                        stream.write(b'HELLO\n')
                        next_hello = now + .5
                    if not recovered and now - started >= 1.5:
                        # Some ESP32 USB bridges hold EN in reset when the port opens.
                        # Recover once, with GPIO0 released; never enter flashing mode.
                        stream.dtr = False
                        stream.rts = True
                        time.sleep(.1)
                        stream.rts = False
                        recovered = True
                    try:
                        message = json.loads(stream.readline(512))
                    except (ValueError, UnicodeError):
                        continue
                    if isinstance(message, dict) and message.get('type') == 'hello':
                        hello = message
                        break
                if not hello:
                    stream.close()
                    raise ValueError('Controlador sem resposta. Feche o Monitor Serial e pressione EN/RESET antes de tentar novamente.')
                if hello.get('version') != VERSION or hello.get('motor_control') != 'direction_only':
                    stream.close()
                    raise ValueError('Firmware incompatível: grave ACOLHE_V2 para Uno com ENA/ENB nos jumpers.')
                with self.lock:
                    self.serial = stream
                    self.port = port
                    self.error = None
                    self.sensor = Telemetry()
                    self.heat = HeatActivity()
                    self.activity = None
                    self.lcd_ok = hello.get('lcd_ok') is True
                    self.lcd_enabled = hello.get('lcd_enabled', True) is True
                    self.board = hello.get('board')
                    self.motor_control = hello['motor_control']
                    self.last_message = time.monotonic()
                    self.end = threading.Event()
                    self.thread = threading.Thread(target=self._run, daemon=True, name='acolhe-serial')
                    self.thread.start()
            except Exception:
                if 'stream' in locals() and stream is not self.serial: stream.close()
                raise
        return self.status()

    def _send(self, command):
        with self.lock:
            if self.serial is None: raise ValueError('Arduino desconectado.')
            self.serial.write((command + '\n').encode('ascii'))

    def _consume(self, message, now):
        if not isinstance(message, dict): return
        kind = message.get('type')
        if kind not in ('sensor', 'hello', 'ack', 'error', 'pong'): return
        with self.lock:
            self.last_message = now
            if kind == 'hello':
                if message.get('version') != VERSION or message.get('motor_control') != 'direction_only':
                    raise ValueError('Firmware incompatível com o controle direto do Uno.')
                self.calibrations.clear()
                self.pending.clear()
                self.tested.clear()
                self.sensor = Telemetry()
                self.lcd_ok = message.get('lcd_ok') is True
                self.lcd_enabled = message.get('lcd_enabled', True) is True
                self.board = message.get('board')
                self.motor_control = message['motor_control']
            elif kind == 'sensor':
                valid = self.sensor.update(message, now)
                if self.heat.update(self.sensor.temperature if valid else None, now):
                    self.activity_id += 1
                    self.activity = {'id': self.activity_id, 'text': 'Vamos aprender a palavra quente e observar a temperatura da sala.', 'temperature': self.sensor.temperature}
            elif kind == 'ack':
                self.ack = message.get('command')
                motor = message.get('motor')
                if self.ack == 'config' and motor in self.pending:
                    self.calibrations[motor] = self.pending.pop(motor)
            elif kind == 'error':
                self.error = str(message.get('message', 'Erro no firmware.'))[:160]

    def _run(self):
        next_ping = 0
        try:
            while not self.end.is_set():
                now = time.monotonic()
                if now >= next_ping:
                    self._send('PING')
                    next_ping = now + .5
                raw = self.serial.readline(512)
                if raw:
                    try: self._consume(json.loads(raw), time.monotonic())
                    except (json.JSONDecodeError, UnicodeError): pass
                if time.monotonic() - self.last_message > 2:
                    raise TimeoutError('Arduino sem resposta por dois segundos.')
        except Exception as exc:
            with self.lock:
                self.error = str(exc)[:180]
                try: self._send('STOP')
                except Exception: pass
                if self.serial: self.serial.close()
                self.serial = None
                self.sensor = Telemetry()
                self.calibrations.clear()
                self.pending.clear()
                self.tested.clear()

    def status(self):
        with self.lock:
            return {'connected': self.serial is not None, 'port': self.port,
                    'version': VERSION if self.serial is not None else None,
                    'sensor': self.sensor.snapshot(time.monotonic()), 'lcd_ok': self.lcd_ok,
                    'lcd_enabled': self.lcd_enabled, 'board': self.board,
                    'motor_control': self.motor_control,
                    'motors_enabled': len(self.calibrations) == 2,
                    'calibrations': dict(self.calibrations), 'error': self.error,
                    'activity': self.activity, 'ack': self.ack,
                    'physical_verified': False}

    @staticmethod
    def _parameters(data):
        if 'pwm' in data: raise ValueError('Este perfil não usa PWM. Atualize a página do painel.')
        motor, duration, direction = (data.get(k) for k in ('motor', 'duration_ms', 'direction'))
        if motor not in ('head', 'arm') or type(duration) is not int or not 1 <= duration <= 150 or type(direction) is not int or direction not in (-1, 1):
            raise ValueError('Motor inválido ou fora dos limites: 1–150 ms, direção -1/1.')
        return {'motor': motor, 'duration_ms': duration, 'direction': direction}

    def test_pulse(self, data):
        params = self._parameters(data)
        if data.get('wiring_confirmed') is not True: raise ValueError('Confirme a montagem antes do pulso supervisionado.')
        return self._pulse(params)

    def command_test(self, motor, cancelled=None):
        """An explicit local operator command authorizes one test, not calibration."""
        params = self._parameters({'motor':motor, 'duration_ms':100, 'direction':1})
        return dict(self._pulse(params,cancelled), **params)

    def _pulse(self, params, cancelled=None):
        with self.lock:
            if cancelled and cancelled(): raise ValueError('Interação interrompida.')
            if time.monotonic() - self.last_gesture < 2: raise ValueError('Aguarde dois segundos entre pulsos.')
            self._send('TEST {motor} {duration_ms} {direction}'.format(**params))
            self.tested[params['motor']] = params
            self.last_gesture = time.monotonic()
        return {'sent': True, 'motor_control':'direction_only', 'physical_verified': False}

    def calibrate(self, data):
        params = self._parameters(data)
        if data.get('observed') is not True: raise ValueError('Confirme que observou o movimento deste motor.')
        with self.lock:
            if self.tested.get(params['motor']) != params:
                raise ValueError('Teste estes mesmos parâmetros antes de registrar movimento observado.')
            self._send('CONFIG {motor} {duration_ms} {direction}'.format(**params))
            self.pending[params['motor']] = params
        return {'pending_ack': True, 'record': params, 'evidence': 'operator_confirmation'}

    def gesture(self, correct, cancelled=None):
        with self.lock:
            if cancelled and cancelled(): return False
            if len(self.calibrations) != 2 or time.monotonic() - self.last_gesture < 2: return False
            self._send('GESTURE ' + ('arm' if correct else 'head'))
            self.last_gesture = time.monotonic()
            return True

    def display(self, state):
        if state not in ('READY', 'LISTEN', 'THINK', 'SPEAK', 'ERROR'): raise ValueError('Estado inválido.')
        with self.lock:
            if self.serial: self._send('STATE ' + state)

    def stop(self):
        with self.lock:
            if self.serial: self._send('STOP')
            self.calibrations.clear()
            self.pending.clear()
            self.tested.clear()

    def _close(self):
        self.end.set()
        if self.thread and self.thread is not threading.current_thread(): self.thread.join(timeout=1)
        with self.lock:
            try: self.stop()
            except Exception: pass
            if self.serial: self.serial.close()
            self.serial = None
            self.sensor = Telemetry()
            self.calibrations.clear()
            self.pending.clear()
            self.port = None
            self.thread = None

    def close(self):
        with self.lifecycle: self._close()
