"""Local academic MVP. Put behind a production proxy/TLS before public deployment."""
import json, os, time, mimetypes, threading
import ipaddress
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote
from app.core import Store, public_lessons
from robot.hardware import RobotConnection
from robot.voice import VoiceAssistant, VoiceError
ROOT=Path(__file__).resolve().parent.parent
STATIC=ROOT/'app'/'static'

class AcolheServer(ThreadingHTTPServer):
 def server_close(self):
  if hasattr(self,'voice'): self.voice.cancel()
  if hasattr(self,'robot'): self.robot.close()
  super().server_close()

class Handler(BaseHTTPRequestHandler):
 def local_control(self):
  host=urlparse('http://'+self.headers.get('Host','')).hostname
  return host in ('127.0.0.1','localhost','::1') and ipaddress.ip_address(self.client_address[0]).is_loopback
 def log_message(self,*args): pass # Do not log questions, session tokens or images.
 def setup(self):
  super().setup(); self.connection.settimeout(15)
 def end_headers(self):
  self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Referrer-Policy','no-referrer')
  self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; media-src 'self' blob:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'")
  self.send_header('Permissions-Policy','microphone=(self), camera=()')
  self.send_header('Cache-Control','no-store'); super().end_headers()
 def reply(self,value,status=200,ctype='application/json; charset=utf-8'):
  body=value if isinstance(value,bytes) else json.dumps(value,ensure_ascii=False).encode('utf-8')
  self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
 def do_GET(self): self.dispatch('GET')
 def do_POST(self): self.dispatch('POST')
 def dispatch(self,method):
  start=time.monotonic()
  with self.server.metrics_lock: self.server.metrics['requests']+=1; self.server.metrics['active']+=1
  try:
   route=urlparse(self.path).path
   if route.startswith('/api/robot/'):
    if not self.local_control():
     self.reply({'error':'Controle do robô disponível somente neste computador.'},403); return
   if method=='POST':
    origin=self.headers.get('Origin'); host=self.headers.get('Host','')
    if origin and urlparse(origin).netloc!=host: self.reply({'error':'Origem não autorizada'},403); return
    if self.headers.get('Content-Type','').split(';')[0]!='application/json': self.reply({'error':'Use JSON'},415); return
    size=int(self.headers.get('Content-Length','0'))
    limit=1048576 if route=='/api/robot/chat' else 8192
    if not 0<size<=limit: self.reply({'error':'Corpo inválido ou muito grande'},413); return
    data=json.loads(self.rfile.read(size))
    if not isinstance(data,dict): raise ValueError('JSON deve ser um objeto')
    self.post(urlparse(self.path).path,data)
   else: self.get(unquote(urlparse(self.path).path))
  except VoiceError as exc:
   self.reply({'error':str(exc),'component':exc.component},409 if exc.component in ('busy','cancelled') else 503)
  except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
   self.reply({'error':str(exc)},400)
  except (BrokenPipeError,ConnectionResetError,TimeoutError): pass
  except Exception:
   with self.server.metrics_lock: self.server.metrics['errors']+=1
   self.reply({'error':'Serviço indisponível. Tente novamente.'},503)
  finally:
   with self.server.metrics_lock:
    self.server.metrics['active']-=1; self.server.metrics['duration']+=time.monotonic()-start
 def get(self,path):
  if path=='/api/robot/status': return self.reply({'robot':self.server.robot.status(),'voice':self.server.voice.status(),'ports':self.server.robot.ports()})
  if path in ('/api/health','/api/v1/health'): return self.reply({'status':'ok','mode':'academic_demo','robot':'serial' if self.server.robot.status()['connected'] else 'simulation','version':'0.1.0'})
  if path=='/api/lessons': return self.reply(public_lessons())
  if path=='/api/summary': return self.reply(self.server.store.summary())
  if path=='/api/gold':
   target=ROOT/'big_data/output/summary.json'
   return self.reply(json.loads(target.read_text(encoding='utf-8')) if target.exists() else {'status':'not_generated','synthetic':True})
  if path=='/api/automation':
   target=ROOT/'rpa/output/progress.json'
   return self.reply(json.loads(target.read_text(encoding='utf-8')) if target.exists() else {'status':'not_generated'})
  if path=='/api/vision/status':
   from vision.service import status
   return self.reply(status())
  if path=='/metrics':
   with self.server.metrics_lock: m=dict(self.server.metrics)
   metrics={'acolhe_requests_total':m['requests'],'acolhe_errors_total':m['errors'],'acolhe_request_duration_seconds_sum':m['duration'],'acolhe_request_duration_seconds_count':m['requests'],'acolhe_active_requests':m['active'],'acolhe_uptime_seconds':time.monotonic()-self.server.started,'acolhe_attempts_total':self.server.store.summary()['attempts']}
   return self.reply((''.join(f'{k} {v}\n' for k,v in metrics.items())).encode(),ctype='text/plain; version=0.0.4; charset=utf-8')
  candidate=(STATIC/('index.html' if path=='/' else path.lstrip('/'))).resolve()
  if not candidate.is_relative_to(STATIC.resolve()) or not candidate.is_file(): return self.reply({'error':'Não encontrado'},404)
  return self.reply(candidate.read_bytes(),ctype=mimetypes.guess_type(str(candidate))[0] or 'application/octet-stream')
 def post(self,path,data):
  if path=='/api/robot/connect':
   try: return self.reply(self.server.robot.connect(data.get('port')))
   except OSError: return self.reply({'error':'Não foi possível abrir a porta. Feche o Monitor Serial e confira o cabo USB.'},503)
  if path=='/api/robot/disconnect':
   self.server.robot.close(); return self.reply({'connected':False})
  if path=='/api/robot/stop':
   self.server.voice.cancel(); self.server.robot.stop(); return self.reply({'stopped':True})
  if path=='/api/robot/state':
   self.server.robot.display(data.get('state')); return self.reply({'ok':True})
  if path=='/api/robot/pulse': return self.reply(self.server.robot.test_pulse(data))
  if path=='/api/robot/calibrate': return self.reply(self.server.robot.calibrate(data))
  if path=='/api/robot/clear':
   self.server.voice.clear(); return self.reply({'cleared':True})
  if path=='/api/robot/chat':
   return self.reply(self.server.voice.chat(data,lambda:self.server.robot.status()['sensor'],self.server.robot.display,on_motor_test=self.server.robot.command_test,on_reaction=self.server.robot.gesture))
  if path=='/api/sessions': return self.reply(self.server.store.session(data.get('language','pt')),201)
  if path=='/api/attempts':
   result=self.server.store.attempt(data.get('session_id'),data.get('lesson_id'),data.get('option'),data.get('request_id'),data.get('language'),include_created=True)
   created=result.pop('created')
   from robot.service import react
   result['robot']=react(result['correct'],present=True)
   if self.local_control() and self.server.robot.status()['connected']:
    try:
     sent=created and self.server.robot.gesture(result['correct'])
     result['robot']={'simulated':False,'physical_verified':False,'status':'command_sent' if sent else 'motors_locked_or_cooldown','action':('arm_wave' if result['correct'] else 'head_wave') if sent else 'stop'}
    except (OSError,ValueError):
     result['robot']={'simulated':False,'physical_verified':False,'status':'communication_error','action':'stop'}
   return self.reply(result)
  if path=='/api/sessions/delete':
   sid=data.get('session_id')
   if not isinstance(sid,str) or len(sid)!=32: raise ValueError('Sessão inválida')
   self.server.store.delete_session(sid); return self.reply({'deleted':True})
  if path=='/api/assistant':
   question=data.get('question'); language=data.get('language','pt')
   if not isinstance(question,str) or not 1<=len(question)<=500 or language not in ('pt','es'): raise ValueError('Pergunta inválida')
   from genai.service import answer
   return self.reply(answer(question,language))
  return self.reply({'error':'Não encontrado'},404)

def create_server(host='127.0.0.1',port=8080,db_path=None):
 server=AcolheServer((host,port),Handler); server.daemon_threads=True
 server.robot=RobotConnection(); server.voice=VoiceAssistant()
 server.store=Store(db_path or Path(os.environ.get('ACOLHE_DB',str(ROOT/'data/acolhe.db'))))
 server.metrics={'requests':0,'errors':0,'duration':0.0,'active':0}; server.metrics_lock=threading.Lock(); server.started=time.monotonic()
 return server
if __name__=='__main__':
 server=create_server(os.getenv('HOST','127.0.0.1'),int(os.getenv('PORT','8080')))
 print(f'Acolhe: http://{server.server_address[0]}:{server.server_port} (Ctrl+C para encerrar)',flush=True)
 try: server.serve_forever()
 except KeyboardInterrupt: pass
 finally: server.server_close()
