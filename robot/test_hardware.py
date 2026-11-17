import unittest
import threading
from unittest.mock import Mock, patch
from robot.hardware import Telemetry, HeatActivity, RobotConnection


class HardwareTests(unittest.TestCase):
    def test_connect_recovers_a_silent_usb_bridge_without_changing_firmware(self):
        class ResetSerial:
            def __init__(self,*args,**kwargs):
                self.dtr=True;self._rts=True;self.reset=False;self.closed=False
            @property
            def rts(self):return self._rts
            @rts.setter
            def rts(self,value):
                if not value and self.dtr is False:self.reset=True
                self._rts=value
            def write(self,data):return len(data)
            def readline(self,*args):
                return b'{"type":"hello","version":"ACOLHE_V2","board":"UNO","motor_control":"direction_only","lcd_ok":true}\n' if self.reset else b''
            def close(self):self.closed=True
        stream=ResetSerial();ticks=[0]
        def now():ticks[0]+=.25;return ticks[0]
        robot=RobotConnection()
        with patch.object(robot,'ports',return_value=[{'device':'COM4'}]),patch('serial.Serial',return_value=stream),patch('robot.hardware.time.monotonic',side_effect=now),patch('robot.hardware.time.sleep'),patch('robot.hardware.threading.Thread'):
            result=robot.connect('COM4')
            self.assertTrue(result['connected']);self.assertTrue(stream.reset)
            robot.close()
    def test_valid_sample_expires_and_invalid_clears(self):
        sensor = Telemetry()
        self.assertTrue(sensor.update({'type': 'sensor', 'valid': True, 'temperature': 26, 'humidity': 55}, 10))
        self.assertEqual(sensor.snapshot(15)['temperature'], 26)
        self.assertFalse(sensor.snapshot(16.1)['valid'])
        sensor.update({'type': 'sensor', 'valid': False}, 17)
        self.assertIsNone(sensor.snapshot(17)['temperature'])

    def test_reject_nonfinite_bool_and_out_of_range(self):
        sensor = Telemetry()
        for t, h in [(float('nan'), 50), (True, 50), (25, 101), (80, 50)]:
            self.assertFalse(sensor.update({'type': 'sensor', 'valid': True, 'temperature': t, 'humidity': h}, 0))
        self.assertFalse(sensor.snapshot(0)['valid'])

    def test_heat_requires_consecutive_samples_rearm_and_cooldown(self):
        heat = HeatActivity()
        for now in [0, 2]: self.assertFalse(heat.update(31, now))
        self.assertTrue(heat.update(31, 4))
        self.assertFalse(heat.update(31, 130))
        heat.update(27, 131)
        for now in [132, 134]: self.assertFalse(heat.update(31, now))
        self.assertTrue(heat.update(31, 136))

    def test_invalid_sample_interrupts_persistence(self):
        heat = HeatActivity()
        heat.update(31, 0); heat.update(31, 2); heat.update(None, 4)
        self.assertFalse(heat.update(31, 6))

    def test_disconnected_is_not_simulation_and_stop_is_idempotent(self):
        robot = RobotConnection()
        self.assertFalse(robot.status()['connected'])
        self.assertFalse(robot.status()['sensor']['valid'])
        robot.stop(); robot.stop(); robot.close()

    def test_calibration_requires_connection_and_valid_limits(self):
        robot = RobotConnection()
        with self.assertRaises(ValueError): robot.calibrate({'motor': 'head', 'duration_ms': 151, 'direction': 1})
        with self.assertRaises(ValueError): robot.calibrate({'motor': 'head', 'duration_ms': 35, 'direction': 1})

    def test_calibration_requires_matching_test_and_firmware_ack(self):
        robot = RobotConnection(); robot.serial = Mock()
        params = {'motor': 'head', 'duration_ms': 35, 'direction': 1, 'observed': True}
        with self.assertRaises(ValueError): robot.calibrate(params)
        robot.test_pulse(dict(params, wiring_confirmed=True))
        robot.calibrate(params)
        self.assertNotIn('head', robot.status()['calibrations'])
        robot._consume({'type': 'ack', 'command': 'config', 'motor': 'head'}, 10)
        self.assertIn('head', robot.status()['calibrations'])
        robot.stop()
        self.assertFalse(robot.status()['motors_enabled'])
        with self.assertRaises(ValueError): robot.calibrate(params)

    def test_reboot_locks_motors_and_invalidates_old_sensor(self):
        robot = RobotConnection()
        robot.sensor.update({'valid': True, 'temperature': 25, 'humidity': 50}, 10)
        robot.calibrations['head'] = {}
        robot._consume({'type': 'hello', 'version': 'ACOLHE_V2', 'motor_control':'direction_only', 'lcd_ok': True}, 11)
        self.assertFalse(robot.sensor.snapshot(11)['valid'])
        self.assertFalse(robot.calibrations)

    def test_uno_identifies_lcd_and_direct_motor_control(self):
        robot=RobotConnection()
        robot._consume({'type':'hello','version':'ACOLHE_V2','board':'UNO','motor_control':'direction_only','lcd_enabled':True,'lcd_ok':True},10)
        self.assertEqual(robot.status()['board'],'UNO')
        self.assertTrue(robot.status()['lcd_enabled'])
        self.assertEqual(robot.status()['motor_control'],'direction_only')

    def test_old_pwm_firmware_is_rejected(self):
        robot=RobotConnection()
        with self.assertRaises(ValueError):robot._consume({'type':'hello','version':'ACOLHE_V1','board':'UNO'},10)

    def test_stale_pwm_request_never_sends_a_pulse(self):
        robot=RobotConnection();robot.serial=Mock()
        with self.assertRaises(ValueError):robot.test_pulse({'motor':'arm','duration_ms':100,'direction':1,'pwm':80,'wiring_confirmed':True})
        robot.serial.write.assert_not_called()

    def test_explicit_command_sends_bounded_test_without_faking_calibration(self):
        robot=RobotConnection();robot.serial=Mock()
        result=robot.command_test('arm')
        robot.serial.write.assert_called_once_with(b'TEST arm 100 1\n')
        self.assertEqual(result['duration_ms'],100)
        self.assertNotIn('pwm',result)
        self.assertEqual(result['motor_control'],'direction_only')
        self.assertFalse(robot.status()['motors_enabled'])
        self.assertFalse(result['physical_verified'])
        with self.assertRaises(ValueError):robot.command_test('head')
        with self.assertRaises(ValueError):robot.command_test('both')

    def test_cancelled_activity_does_not_send_gesture_even_when_calibrated(self):
        robot=RobotConnection();robot.serial=Mock();robot.calibrations={'head':{},'arm':{}}
        self.assertFalse(robot.gesture(True,cancelled=lambda:True))
        robot.serial.write.assert_not_called()
        self.assertTrue(robot.gesture(False))
        robot.serial.write.assert_called_once_with(b'GESTURE head\n')

    def test_stop_prevents_a_queued_command_from_sending_a_late_pulse(self):
        robot=RobotConnection();robot.serial=Mock();cancelled=threading.Event();errors=[]
        def dispatch():
            try:robot.command_test('arm',cancelled=cancelled.is_set)
            except Exception as exc:errors.append(exc)
        with robot.lock:
            worker=threading.Thread(target=dispatch);worker.start()
            cancelled.set();robot.stop()
        worker.join(timeout=2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(errors),1);self.assertIsInstance(errors[0],ValueError)
        self.assertFalse(any(call.args[0].startswith(b'TEST ') for call in robot.serial.write.call_args_list))


if __name__ == '__main__': unittest.main()
