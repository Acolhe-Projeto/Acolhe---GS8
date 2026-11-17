import base64
import json
from unittest.mock import patch
import urllib.error
import unittest
from tests.test_http import HttpTests


class RobotHttpTests(unittest.TestCase):
    setUp = HttpTests.setUp
    tearDown = HttpTests.tearDown
    request = HttpTests.request
    def test_remote_lesson_request_never_actuates_physical_robot(self):
        sid=json.load(self.request('/api/sessions',{'language':'pt'}))['id']
        with patch.object(self.server.robot,'status',return_value={'connected':True}), patch.object(self.server.robot,'gesture') as gesture:
            self.request('/api/attempts',{'session_id':sid,'lesson_id':'casa','option':0,'request_id':'remote'}, {'Content-Type':'application/json','Host':'attacker.example'}).close()
        gesture.assert_not_called()

    def test_duplicate_attempt_does_not_repeat_gesture(self):
        sid=json.load(self.request('/api/sessions',{'language':'pt'}))['id']
        data={'session_id':sid,'lesson_id':'casa','option':0,'request_id':'same'}
        with patch.object(self.server.robot,'status',return_value={'connected':True}), patch.object(self.server.robot,'gesture',return_value=True) as gesture:
            self.request('/api/attempts',data).close(); self.request('/api/attempts',data).close()
        self.assertEqual(gesture.call_count,1)

    def test_robot_status_exposes_real_disconnected_state(self):
        result = json.load(self.request('/api/robot/status'))
        self.assertFalse(result['robot']['connected'])
        self.assertFalse(result['robot']['sensor']['valid'])
        self.assertIn('voice', result)

    def test_explicit_chat_dispatches_only_one_bounded_motor_test(self):
        from unittest.mock import Mock
        self.server.robot.serial=Mock()
        with patch.object(self.server.voice,'_speak',return_value='audio'),patch.object(self.server.voice,'_generate') as generate:
            result=json.load(self.request('/api/robot/chat',{'text':'Acolhe, mova o braço'}))
        generate.assert_not_called()
        self.server.robot.serial.write.assert_any_call(b'TEST arm 100 1\n')
        self.assertEqual(result['mode'],'motor_test')
        self.assertFalse(self.server.robot.status()['motors_enabled'])
        self.assertFalse(result['motor_test']['physical_verified'])
        self.assertNotIn('pwm',result['motor_test'])

    def test_guided_practice_uses_calibrated_gesture_callback(self):
        with patch.object(self.server.voice,'_speak',return_value='audio'),patch.object(self.server.robot,'gesture',return_value=False) as gesture:
            json.load(self.request('/api/robot/chat',{'text':'Vamos praticar'}))
            result=json.load(self.request('/api/robot/chat',{'text':'olá'}))
        self.assertEqual(result['mode'],'guided_practice')
        self.assertEqual(gesture.call_args.args,(True,))
        self.assertFalse(result['motor_reaction']['sent'])

    def test_robot_routes_reject_remote_host(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request('/api/robot/stop', {}, {'Content-Type': 'application/json', 'Host': 'attacker.example'})
        self.assertEqual(caught.exception.code, 403)

    def test_robot_chat_supports_pcm_without_expanding_other_routes(self):
        pcm = base64.b64encode(b'\0\0' * 16000).decode()
        with patch.object(self.server.voice, 'chat', return_value={'answer': 'Olá', 'audio_wav': None}) as chat:
            self.assertEqual(json.load(self.request('/api/robot/chat', {'pcm16': pcm}))['answer'], 'Olá')
            self.assertEqual(chat.call_args.args[1]()['valid'], False)
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request('/api/assistant', {'question': 'x' * 9000})
        self.assertEqual(caught.exception.code, 413)

    def test_stop_cancels_voice_and_resets_hardware(self):
        with patch.object(self.server.voice, 'cancel') as cancel, patch.object(self.server.robot, 'stop') as stop:
            self.assertTrue(json.load(self.request('/api/robot/stop', {}))['stopped'])
        cancel.assert_called_once(); stop.assert_called_once()

    def test_robot_state_does_not_accept_commands(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request('/api/robot/state', {'state': 'GESTURE arm'})
        self.assertEqual(caught.exception.code, 400)

    def test_robot_page_available(self):
        with self.request('/robo.html') as response:
            self.assertIn(b'robot.js', response.read())


del HttpTests

if __name__ == '__main__':
    unittest.main()
