from django.test import TestCase
from designthinking.api import *
from designthinking.dbconnection import *
from designthinking.audio import *

# Create your tests here.
class WatsonAssistantTestCase(TestCase):

    def test_chatbot_create_session_success(self):
        response = testCreate()
        self.assertEqual(response, 201)

class DatabaseTestCase(TestCase):

    def test_connection_is_active(self):
        response = connectionTest()
        self.assertEqual(response, True)

class TTSTestCase(TestCase):
    def test_TTS_voice_success(self):
        response = testGetVoice()
        self.assertEqual(response, 200)