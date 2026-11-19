import subprocess
import unittest
from unittest.mock import Mock, patch
import urllib.error
from app import launcher


class LauncherTests(unittest.TestCase):
    tags={'models':[{'name':'qwen3:4b'}]}

    def test_existing_acolhe_is_opened_without_restarting_hardware(self):
        with patch('sys.argv',['launcher']),patch.dict('os.environ',{'HOST':'127.0.0.1','PORT':'8080'}),patch.object(launcher,'prepare_services'),patch.object(launcher,'port_open',return_value=True),patch.object(launcher,'request_json',side_effect=[{'mode':'academic_demo'},{'voice':{}}]),patch.object(launcher.webbrowser,'open') as browser,patch('app.server.create_server') as create:
            self.assertEqual(launcher.main(),0)
        create.assert_not_called()
        browser.assert_called_once_with('http://127.0.0.1:8080/robo.html')

    def test_new_server_is_closed_on_interruption(self):
        server=Mock();server.serve_forever.side_effect=KeyboardInterrupt
        with patch('sys.argv',['launcher']),patch.object(launcher,'prepare_services'),patch.object(launcher,'port_open',return_value=False),patch.object(launcher.threading,'Timer'),patch('app.server.create_server',return_value=server):
            self.assertEqual(launcher.main(),0)
        server.server_close.assert_called_once()

    def test_invalid_service_response_is_reported(self):
        with patch.object(launcher,'request_json',return_value=[]):
            with self.assertRaisesRegex(RuntimeError,'inválida'): launcher.ensure_ollama('qwen3:4b')

    def test_running_ollama_is_reused_and_model_warmed(self):
        with patch.object(launcher,'request_json',side_effect=[self.tags,{'done':True}]) as request,patch.object(launcher,'start_ollama') as start:
            launcher.ensure_ollama('qwen3:4b')
        start.assert_not_called()
        self.assertEqual(request.call_args.kwargs['data']['model'],'qwen3:4b')

    def test_stopped_ollama_is_started_before_model_is_loaded(self):
        child=Mock();child.poll.return_value=None
        with patch.object(launcher,'request_json',side_effect=[urllib.error.URLError('offline'),self.tags,{'done':True}]),patch.object(launcher,'port_open',return_value=False),patch.object(launcher,'start_ollama',return_value=child) as start:
            launcher.ensure_ollama('qwen3:4b')
        start.assert_called_once()

    def test_missing_model_is_reported_without_automatic_download(self):
        with patch.object(launcher,'request_json',return_value={'models':[]}) as request:
            with self.assertRaisesRegex(RuntimeError,'ollama pull qwen3:4b'):
                launcher.ensure_ollama('qwen3:4b')
        self.assertEqual(request.call_count,1)

    def test_unresponsive_service_is_not_duplicated(self):
        with patch.object(launcher,'request_json',side_effect=urllib.error.URLError('timeout')),patch.object(launcher,'port_open',return_value=True),patch.object(launcher,'start_ollama') as start:
            with self.assertRaisesRegex(RuntimeError,'11434'): launcher.ensure_ollama('qwen3:4b')
        start.assert_not_called()

    def test_failed_model_load_prevents_false_ready_message(self):
        with patch.object(launcher,'request_json',side_effect=[self.tags,urllib.error.URLError('load failed')]):
            with self.assertRaisesRegex(RuntimeError,'carregar'): launcher.ensure_ollama('qwen3:4b')

    def test_ollama_subprocess_is_hidden_and_output_is_redirected(self):
        with patch.object(launcher.shutil,'which',return_value='ollama.exe'),patch.object(launcher.subprocess,'Popen') as spawn:
            launcher.start_ollama()
        self.assertEqual(spawn.call_args.args[0],['ollama.exe','serve'])
        self.assertNotEqual(spawn.call_args.kwargs['stdout'],subprocess.PIPE)
        self.assertEqual(spawn.call_args.kwargs['creationflags'],getattr(subprocess,'CREATE_NO_WINDOW',0))
