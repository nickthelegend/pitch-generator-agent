import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

import main


class AgentApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)

    @patch('main.generate_slides')
    def test_generate_slides(self, mock_generate):
        mock_generate.return_value = []
        resp = self.client.post('/tools/slides/generate', json={
            'topic': 'AI',
            'count': 1,
            'style': 'Modern'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slides', resp.json())

    @patch('main.generate_tts')
    def test_tts(self, mock_tts):
        mock_tts.return_value = 'dGVzdA=='
        resp = self.client.post('/tools/tts', json={
            'script': [{'speaker': 'Presenter', 'line': 'Hello'}],
            'language': 'en-US'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['audio'], 'dGVzdA==')

    @patch('main.render_video')
    @patch('main.pinata_upload')
    def test_video_render_with_ipfs(self, mock_pinata, mock_render):
        mock_render.return_value = ('/tmp/video.mp4', 'video.mp4')
        mock_pinata.return_value = {
            'ipfsHash': 'QmTest',
            'ipfsUrl': 'ipfs://QmTest',
            'gatewayUrl': 'https://gateway.pinata.cloud/ipfs/QmTest'
        }
        resp = self.client.post('/tools/video/render', json={
            'topic': 'AI',
            'slides': [],
            'format': '16:9',
            'fps': 30,
            'outputFormat': 'mp4',
            'generateAudio': False,
            'ttsLanguage': 'en-US'
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body['ipfsUrl'], 'ipfs://QmTest')
        self.assertEqual(body['gatewayUrl'], 'https://gateway.pinata.cloud/ipfs/QmTest')


if __name__ == '__main__':
    unittest.main()
