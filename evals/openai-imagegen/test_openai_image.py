"""Behavior tests for skills/media/openai-imagegen/scripts/openai_image.py.

Two seams: the CLI's --dry-run output, and real HTTP calls against a local fake
OpenAI server reached through OPENAI_BASE_URL. Run from the repo root:

    python evals/openai-imagegen/test_openai_image.py
"""
from __future__ import annotations

import base64
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'skills' / 'media' / 'openai-imagegen' / 'scripts' / 'openai_image.py'
PNG_BYTES = b'\x89PNG\r\n\x1a\nfake-image-bytes'


def run(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = {k: v for k, v in os.environ.items() if k not in ('OPENAI_API_KEY', 'OPENAI_BASE_URL')}
    full_env.update(env or {})
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=full_env,
                          timeout=60)


def dry_run(*args: str) -> dict:
    result = run('--dry-run', '--prompt', 'a red fox', *args)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class DryRunTest(unittest.TestCase):
    def test_defaults_to_gpt_image_2_6_flare_generation(self):
        request = dry_run()
        self.assertEqual(request['endpoint'], '/images/generations')
        self.assertEqual(request['body']['model'], 'gpt-image-2.6-flare')
        self.assertEqual(request['body']['prompt'], 'a red fox')
        self.assertEqual(request['body']['quality'], 'high')

    def test_aspect_ratio_maps_to_a_supported_size(self):
        cases = {'1:1': '1024x1024', '3:2': '1536x1024', '2:3': '1024x1536', '16:9': '1536x864',
                 '9:16': '864x1536'}
        for ratio, size in cases.items():
            with self.subTest(ratio=ratio):
                self.assertEqual(dry_run('--aspect-ratio', ratio)['body']['size'], size)

    def test_explicit_size_wins_and_is_validated(self):
        self.assertEqual(dry_run('--size', '2048x1152')['body']['size'], '2048x1152')
        bad = run('--dry-run', '--prompt', 'x', '--size', '1000x1000')
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('multiple of 16', bad.stderr)

    def test_optional_parameters_are_sent_only_when_set(self):
        body = dry_run()['body']
        for key in ('background', 'complexity', 'output_compression', 'moderation'):
            self.assertNotIn(key, body)
        body = dry_run('--complexity', 'low', '--background', 'transparent', '--moderation', 'low')['body']
        self.assertEqual((body['complexity'], body['background'], body['moderation']), ('low', 'transparent', 'low'))

    def test_transparent_background_rejects_jpeg(self):
        bad = run('--dry-run', '--prompt', 'x', '--background', 'transparent', '--output-format', 'jpeg')
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('transparent', bad.stderr)

    def test_reference_images_switch_to_the_edits_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref = pathlib.Path(tmp, 'ref.png')
            ref.write_bytes(PNG_BYTES)
            request = dry_run('--ref', str(ref))
        self.assertEqual(request['endpoint'], '/images/edits')
        self.assertEqual(request['files'], [{'field': 'image[]', 'path': str(ref)}])

    def test_missing_key_explains_how_to_set_it(self):
        result = run('--prompt', 'x', env={'USERPROFILE': tempfile.gettempdir(), 'HOME': tempfile.gettempdir(),
                                           'OPENAI_API_KEY_SKIP_REGISTRY': '1'})
        self.assertEqual(result.returncode, 2)
        self.assertIn('OPENAI_API_KEY', result.stderr)


class FakeOpenAI:
    """Local stand-in for api.openai.com. `responses` maps a model id to an HTTP status."""

    def __init__(self, responses: dict[str, int] | None = None):
        self.responses = responses or {}
        self.requests: list[dict] = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                raw = self.rfile.read(int(self.headers['Content-Length']))
                ctype = self.headers['Content-Type']
                if ctype.startswith('application/json'):
                    model = json.loads(raw)['model']
                else:
                    model = raw.split(b'name="model"\r\n\r\n', 1)[1].split(b'\r\n', 1)[0].decode()
                fake.requests.append({'path': self.path, 'type': ctype, 'raw': raw, 'model': model,
                                      'auth': self.headers['Authorization']})
                status = fake.responses.get(model, 200)
                if status == 200:
                    body = {'created': 1, 'data': [{'b64_json': base64.b64encode(PNG_BYTES).decode()}],
                            'usage': {'input_tokens': 10, 'output_tokens': 1000, 'total_tokens': 1010}}
                else:
                    body = {'error': {'message': f'status {status} for {model}'}}
                data = json.dumps(body).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = HTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base_url = f'http://127.0.0.1:{self.server.server_port}/v1'

    def close(self):
        self.server.shutdown()


class LiveCallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = pathlib.Path(self.tmp.name, 'out')

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, fake: FakeOpenAI, *args: str) -> subprocess.CompletedProcess:
        return run('--prompt', 'a red fox', '--out', str(self.out), '--name', 'fox', '--json', *args,
                   env={'OPENAI_API_KEY': 'sk-test', 'OPENAI_BASE_URL': fake.base_url})

    def test_generation_saves_the_returned_image(self):
        fake = FakeOpenAI()
        try:
            result = self.call(fake)
        finally:
            fake.close()
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        saved = pathlib.Path(summary['files'][0])
        self.assertEqual(saved.name, 'fox.png')
        self.assertEqual(saved.read_bytes(), PNG_BYTES)
        self.assertEqual(summary['model'], 'gpt-image-2.6-flare')
        self.assertEqual(summary['usage']['output_tokens'], 1000)
        self.assertAlmostEqual(summary['estimated_cost_usd'], 0.03005)
        self.assertEqual(fake.requests[0]['path'], '/v1/images/generations')
        self.assertEqual(fake.requests[0]['auth'], 'Bearer sk-test')

    def test_edit_uploads_reference_images_as_multipart(self):
        ref = pathlib.Path(self.tmp.name, 'ref.png')
        ref.write_bytes(PNG_BYTES)
        fake = FakeOpenAI()
        try:
            result = self.call(fake, '--ref', str(ref), '--ref', str(ref))
        finally:
            fake.close()
        self.assertEqual(result.returncode, 0, result.stderr)
        request = fake.requests[0]
        self.assertEqual(request['path'], '/v1/images/edits')
        self.assertTrue(request['type'].startswith('multipart/form-data; boundary='))
        self.assertEqual(request['raw'].count(b'name="image[]"; filename="ref.png"'), 2)
        self.assertIn(PNG_BYTES, request['raw'])
        self.assertIn(b'name="prompt"\r\n\r\na red fox', request['raw'])

    def test_unavailable_model_falls_back_to_the_next_one(self):
        fake = FakeOpenAI({'gpt-image-2.6-flare': 404})
        try:
            result = self.call(fake)
        finally:
            fake.close()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['model'], 'gpt-image-2.5-flare')

    def test_request_errors_stop_without_fallback(self):
        for status in (400, 401):
            with self.subTest(status=status):
                fake = FakeOpenAI({'gpt-image-2.6-flare': status})
                try:
                    result = self.call(fake)
                finally:
                    fake.close()
                self.assertEqual(result.returncode, 1)
                self.assertEqual([r['model'] for r in fake.requests], ['gpt-image-2.6-flare'])
                self.assertIn(f'HTTP {status}', result.stderr)


if __name__ == '__main__':
    unittest.main()
