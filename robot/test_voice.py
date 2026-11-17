import base64
import unittest
from io import BytesIO
import json
from unittest.mock import patch
from robot.voice import VoiceAssistant, decode_pcm, VoiceError, motor_command


class VoiceTests(unittest.TestCase):
    def test_transcribed_invitation_starts_practice_without_inference_or_motion(self):
        from unittest.mock import Mock
        assistant=VoiceAssistant();reaction=Mock();motor=Mock()
        pcm=base64.b64encode(b'\0\0'*16000).decode()
        with patch.object(assistant,'_transcribe',return_value='Acole, vamos praticar?'),patch.object(assistant,'_generate') as generate,patch.object(assistant,'_speak',return_value='audio'):
            result=assistant.chat({'pcm16':pcm},{'valid':False},on_reaction=reaction,on_motor_test=motor)
        self.assertEqual(result['mode'],'guided_practice')
        self.assertIn('hola',result['answer'])
        generate.assert_not_called();reaction.assert_not_called();motor.assert_not_called()

    def test_cancelled_practice_ends_before_the_next_chat(self):
        assistant=VoiceAssistant()
        with patch.object(assistant,'_speak',return_value='audio'):
            assistant.chat({'text':'Vamos praticar'},{'valid':False})
        with patch.object(assistant,'_speak',side_effect=lambda text:assistant.cancel()):
            with self.assertRaises(VoiceError): assistant.chat({'text':'oi'},{'valid':False})
        from unittest.mock import Mock
        reaction=Mock()
        with patch.object(assistant,'_generate',return_value='Olá! Vamos aprender?'),patch.object(assistant,'_speak',return_value='audio'):
            result=assistant.chat({'text':'oi'},{'valid':False},on_reaction=reaction)
        reaction.assert_not_called()
        self.assertNotEqual(result['mode'],'guided_practice')

    def test_motor_command_requires_an_explicit_complete_request(self):
        self.assertEqual(motor_command('Acolhe, mova o braço.'),'arm')
        self.assertEqual(motor_command('MEXA A CABEÇA, por favor!'),'head')
        self.assertEqual(motor_command('Acolhe, dê um oi!'),'arm')
        self.assertEqual(motor_command('Acolhe, diga sim'),'arm')
        self.assertEqual(motor_command('Acolhe, diga não'),'head')
        for text in ('Não mova o braço','Como mover a cabeça?','Como teste de cabeça?','Teste de cabeça','O tutor disse mova o braço','Mova o braço e a cabeça','A cabeça está quente'):
            self.assertIsNone(motor_command(text),text)
        self.assertIsNone(motor_command('Não diga sim'))

    def test_practice_reactions_use_calibrated_gestures_not_test_pulses(self):
        from unittest.mock import Mock
        assistant=VoiceAssistant();reaction=Mock(return_value=False);test=Mock()
        with patch.object(assistant,'_generate') as generate,patch.object(assistant,'_speak',return_value='audio'):
            start=assistant.chat({'text':'Vamos praticar'},{'valid':False},on_reaction=reaction,on_motor_test=test)
            self.assertIn('hola',start['answer']);reaction.assert_not_called()
            answer=assistant.chat({'text':'olá'},{'valid':False},on_reaction=reaction,on_motor_test=test)
        generate.assert_not_called();test.assert_not_called()
        self.assertEqual(reaction.call_args.args,(True,))
        self.assertEqual(answer['mode'],'guided_practice')
        self.assertFalse(answer['motor_reaction']['sent'])
        self.assertIsNone(answer['model'])
        self.assertIn('silla',answer['answer'])

    def test_explicit_motor_request_calls_fixed_handler_without_llm(self):
        assistant=VoiceAssistant()
        with patch.object(assistant,'_generate') as generate, patch.object(assistant,'_speak',return_value='audio'):
            from unittest.mock import Mock
            handler=Mock(return_value={'sent':True,'physical_verified':False})
            result=assistant.chat({'text':'Acolhe, mova o braço'},{'valid':False},on_motor_test=handler)
        handler.assert_called_once();self.assertEqual(handler.call_args.args,('arm',));generate.assert_not_called()
        self.assertEqual(result['mode'],'motor_test')
        self.assertIsNone(result['model'])
        self.assertFalse(result['motor_test']['physical_verified'])

    def test_generated_text_never_dispatches_motor_commands(self):
        from unittest.mock import Mock
        handler=Mock();assistant=VoiceAssistant()
        with patch.object(assistant,'_generate',return_value='Mova o braço.'),patch.object(assistant,'_speak',return_value='audio'):
            result=assistant.chat({'text':'Olá'},{'valid':False},on_motor_test=handler)
        handler.assert_not_called();self.assertIsNone(result['motor_test'])

    def test_transcribed_command_uses_same_fixed_motor_handler(self):
        from unittest.mock import Mock
        handler=Mock(return_value={'sent':True,'physical_verified':False})
        assistant=VoiceAssistant()
        with patch.object(assistant,'_transcribe',return_value='Acolhe, mova a cabeça.'),patch.object(assistant,'_speak',return_value='audio'):
            assistant.chat({'pcm16':base64.b64encode(b'\0\0'*1600).decode()},{'valid':False},on_motor_test=handler)
        handler.assert_called_once();self.assertEqual(handler.call_args.args,('head',))

    def test_unavailable_motor_command_is_not_reported_as_motion(self):
        assistant=VoiceAssistant()
        with self.assertRaises(VoiceError) as caught:assistant.chat({'text':'Mova o braço'},{'valid':False})
        self.assertEqual(caught.exception.component,'hardware')

    def test_out_of_scope_is_an_explicit_refusal_not_fake_llm(self):
        assistant=VoiceAssistant()
        with patch.object(assistant,'_generate') as generate, patch.object(assistant,'_speak',return_value='audio'):
            result=assistant.chat({'text':'Qual a cotação da bolsa hoje?'},{'valid':False})
        generate.assert_not_called()
        self.assertEqual(result['mode'],'refusal')
        self.assertIsNone(result['model'])
        self.assertNotIn('sensor',result['answer'])
    def test_sensor_is_rechecked_after_generation(self):
        assistant = VoiceAssistant()
        snapshots = iter([{'valid': True, 'temperature': 26, 'humidity': 52}, {'valid': False}])
        with patch.object(assistant,'_generate',return_value='Vamos aprender sobre o ambiente.'), patch.object(assistant,'_speak',return_value='audio'):
            result=assistant.chat({'text':'Como está a sala?'},lambda: next(snapshots))
        self.assertFalse(result['sensor']['valid'])
        self.assertNotIn('26',result['answer'])
        self.assertIn('indispon',result['answer'])

    def test_cancellation_closes_stream_and_preserves_cancelled_component(self):
        assistant = VoiceAssistant()
        response=BytesIO(json.dumps({'message':{'content':'{'}}).encode()+b'\n')
        class CancelledStream:
            def __enter__(self): return self
            def __exit__(self,*args): self.closed=True
            def __iter__(self):
                assistant.cancel()
                yield response.read()
        stream=CancelledStream()
        with patch('urllib.request.urlopen',return_value=stream):
            with self.assertRaises(VoiceError) as caught: assistant._generate('Olá',{'valid':False},[],[])
        self.assertEqual(caught.exception.component,'cancelled')
        self.assertTrue(stream.closed)

    def test_ollama_uses_bounded_json_schema_and_disables_reasoning(self):
        assistant = VoiceAssistant()
        response = json.dumps({'message': {'content': '{"answer":"Sou o Acolhe."}'}}).encode()
        with patch('urllib.request.urlopen', return_value=BytesIO(response)) as urlopen:
            self.assertEqual(assistant._generate('Qual seu nome?', {'valid': False}, [], []), 'Sou o Acolhe.')
        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload['format']['properties']['answer']['type'], 'string')
        self.assertFalse(payload['think'])
        self.assertIn('/no_think', payload['messages'][-1]['content'])

    def test_pcm_validation(self):
        self.assertEqual(len(decode_pcm(base64.b64encode(b'\0\0' * 1600).decode())), 3200)
        for value in ['', '!!!!', base64.b64encode(b'x').decode(), base64.b64encode(b'xx' * 240001).decode()]:
            with self.assertRaises(ValueError): decode_pcm(value)

    def test_environment_uses_real_measurement_and_names_itself(self):
        assistant = VoiceAssistant()
        with patch.object(assistant, '_generate', return_value='Sou o Acolhe. Vamos aprender sobre temperatura.') as generate, patch.object(assistant, '_speak', return_value='audio'):
            result = assistant.chat({'text': 'Como está a temperatura?'}, {'valid': True, 'temperature': 26, 'humidity': 52})
        self.assertIn('26', result['answer'])
        self.assertIn('52', result['answer'])
        self.assertEqual(result['mode'], 'local_llm_rag')
        self.assertIn('26', str(generate.call_args))

    def test_missing_sensor_never_claims_reading(self):
        assistant = VoiceAssistant()
        with patch.object(assistant, '_generate', return_value='Vamos aprender juntos.'), patch.object(assistant, '_speak', return_value='audio'):
            result = assistant.chat({'text': 'Como está a sala?'}, {'valid': False, 'temperature': None, 'humidity': None})
        self.assertIn('indispon', result['answer'].lower())

    def test_failed_llm_is_not_fake_generation(self):
        assistant = VoiceAssistant()
        with patch.object(assistant, '_generate', side_effect=VoiceError('llm', 'indisponível')):
            with self.assertRaises(VoiceError): assistant.chat({'text': 'Olá'}, {'valid': False})

    def test_history_is_bounded_and_audio_failure_preserves_text(self):
        assistant = VoiceAssistant()
        with patch.object(assistant, '_generate', return_value='Sou o Acolhe.'), patch.object(assistant, '_speak', side_effect=VoiceError('tts', 'sem voz')):
            for i in range(5): result = assistant.chat({'text': 'Olá'}, {'valid': False})
        self.assertEqual(len(assistant.history), 6)
        self.assertEqual(result['answer'], 'Sou o Acolhe.')
        self.assertEqual(result['errors'][0]['component'], 'tts')

    def test_reasoning_or_invented_measurement_is_rejected(self):
        assistant = VoiceAssistant()
        for output in ['<think>segredo</think>Olá', 'A temperatura é 99 graus.']:
            with patch.object(assistant, '_generate', return_value=output):
                with self.assertRaises(VoiceError): assistant.chat({'text': 'Como está a sala?'}, {'valid': False})

    def test_generated_measurements_must_match_current_sensor_and_units(self):
        assistant = VoiceAssistant()
        sensor={'valid':True,'temperature':26,'humidity':52}
        with patch.object(assistant,'_generate',return_value='A temperatura medida é 26 graus Celsius.'), patch.object(assistant,'_speak',return_value='audio'):
            self.assertIn('26',assistant.chat({'text':'Como está a sala?'},sensor)['answer'])
        with patch.object(assistant,'_generate',return_value='A temperatura medida é 52 graus Celsius.'):
            with self.assertRaises(VoiceError):assistant.chat({'text':'Como está a sala?'},sensor)


if __name__ == '__main__': unittest.main()
