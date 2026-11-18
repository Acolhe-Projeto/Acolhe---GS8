import http.client, json, tempfile, threading, unittest, urllib.request, urllib.error
from unittest.mock import patch
from pathlib import Path
from app.server import create_server

class HttpTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.server=create_server('127.0.0.1',0,Path(self.tmp.name)/'db.sqlite')
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start(); self.base='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):
  self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()
 def request(self,path,data=None,headers=None):
  req=urllib.request.Request(self.base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers or {'Content-Type':'application/json'})
  return urllib.request.urlopen(req)
 def test_health_and_static(self):
  self.assertEqual(json.load(self.request('/api/health'))['status'],'ok')
  with self.request('/') as r: self.assertEqual(r.status,200); self.assertIn('Content-Security-Policy',r.headers)
 def test_occupied_port_cannot_serve_a_second_instance(self):
  with self.assertRaises(OSError):
   create_server('127.0.0.1',self.server.server_port,Path(self.tmp.name)/'second.sqlite')
 def test_session_attempt_http(self):
  session=json.load(self.request('/api/sessions',{'language':'es'}))
  attempt=json.load(self.request('/api/attempts',{'session_id':session['id'],'lesson_id':'casa','option':0,'request_id':'one'}))
  self.assertTrue(attempt['correct']); self.assertTrue(attempt['robot']['simulated'])
 def test_metrics_four_golden_signals_idle_saturation_is_zero(self):
  self.request('/api/health').read()
  with urllib.request.urlopen(self.base+'/metrics') as r: text=r.read().decode()
  m=dict(line.split(' ') for line in text.strip().splitlines())
  for k in ('acolhe_request_duration_seconds_sum','acolhe_requests_total','acolhe_errors_total','acolhe_active_requests'): self.assertIn(k,m)
  self.assertEqual(float(m['acolhe_active_requests']),0)  # the scrape must not count itself
  self.assertGreaterEqual(float(m['acolhe_requests_total']),2)
 def test_cross_origin_blocked(self):
  with self.assertRaises(urllib.error.HTTPError) as caught: self.request('/api/sessions',{'language':'pt'},{'Content-Type':'application/json','Origin':'https://evil.example'})
  self.assertEqual(caught.exception.code,403)
 def test_traversal_blocked(self):
  with self.assertRaises(urllib.error.HTTPError): self.request('/%2e%2e/app/core.py')
 def test_invalid_json(self):
  req=urllib.request.Request(self.base+'/api/sessions',data=b'{',headers={'Content-Type':'application/json'})
  with self.assertRaises(urllib.error.HTTPError) as caught: urllib.request.urlopen(req)
  self.assertEqual(caught.exception.code,400)
 def test_answers_not_disclosed(self):
  lessons=json.load(self.request('/api/lessons')); self.assertNotIn('answer',lessons[0])

 def upload(self,body=b'\x89PNG\r\n\x1a\nexample',content_type='image/png',origin=None):
  headers={'Content-Type':content_type}
  if origin: headers['Origin']=origin
  return urllib.request.urlopen(urllib.request.Request(self.base+'/api/vision/predict',data=body,headers=headers))

 def test_vision_upload_contract_and_no_storage(self):
  result={'detections':[{'class':'cup','pt':'copo','es':'vaso','confidence':0.9,'xyxy':[0,0,10,10]}],'mode':'custom_model','stores_image':False}
  with patch('vision.service.predict',return_value=result) as predict:
   self.assertEqual(json.load(self.upload()),result)
   predict.assert_called_once_with(b'\x89PNG\r\n\x1a\nexample')
  self.assertEqual({p.name for p in Path(self.tmp.name).iterdir()},{'db.sqlite'})

 def test_vision_absent_model_returns_503(self):
  from vision.service import ModelUnavailable
  with patch('vision.service.predict',side_effect=ModelUnavailable('absent')):
   with self.assertRaises(urllib.error.HTTPError) as caught: self.upload()
  self.assertEqual(caught.exception.code,503)
  self.assertFalse(json.load(caught.exception)['stores_image'])

 def test_vision_upload_rejects_type_signature_size_and_origin(self):
  cases=[(b'plain','text/plain',None,415),(b'plain','image/png',None,400),
         (b'','image/png',None,413),
         (b'\x89PNG\r\n\x1a\n','image/png','https://evil.example',403)]
  with patch('vision.service.predict') as predict:
   for body,content_type,origin,status in cases:
    with self.subTest(status=status):
     with self.assertRaises(urllib.error.HTTPError) as caught: self.upload(body,content_type,origin)
     self.assertEqual(caught.exception.code,status)
   predict.assert_not_called()

 def test_vision_rejects_large_declared_length_before_reading(self):
  connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
  try:
   connection.putrequest('POST','/api/vision/predict')
   connection.putheader('Content-Type','image/png')
   connection.putheader('Content-Length',str(8*1024*1024+1))
   connection.endheaders()
   self.assertEqual(connection.getresponse().status,413)
  finally: connection.close()

 def test_vision_corrupt_image_returns_400(self):
  with patch('vision.service.predict',side_effect=OSError('bad image')):
   with self.assertRaises(urllib.error.HTTPError) as caught: self.upload()
  self.assertEqual(caught.exception.code,400)

 def test_language_switch_preserves_attempt_history(self):
  from rpa.robot import generate_report
  sid=json.load(self.request('/api/sessions',{'language':'pt'}))['id']
  for language,request_id in [('pt','first'),('es','second')]:
   json.load(self.request('/api/attempts',{'session_id':sid,'lesson_id':'casa','option':0,'request_id':request_id,'language':language}))
  report=generate_report(self.server.store.path,Path(self.tmp.name)/'report')
  self.assertEqual(report['by_language'],[{'language':'es','attempts':1,'correct':1},{'language':'pt','attempts':1,'correct':1}])
  self.assertEqual(report['totals']['sessions'],1)
  json.load(self.request('/api/sessions/delete',{'session_id':sid}))
  self.assertEqual(self.server.store.summary()['attempts'],0)

 def test_invalid_attempt_language_is_rejected(self):
  sid=json.load(self.request('/api/sessions',{'language':'pt'}))['id']
  with self.assertRaises(urllib.error.HTTPError) as caught:
   self.request('/api/attempts',{'session_id':sid,'lesson_id':'casa','option':0,'request_id':'bad-language','language':'xx'})
  self.assertEqual(caught.exception.code,400)
  self.assertEqual(self.server.store.summary()['attempts'],0)
