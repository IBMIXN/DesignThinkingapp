from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import simpleaudio as sa

apikey = "FnR0IEGhCkL_t20v1yphYJruUSgIatOmeSo_ba7WDk8u"
url = "https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/6f715e03-1d19-4bb9-80a9-f5c751abf555"

authenticator = IAMAuthenticator(apikey)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url)
voiceModel = 'en-GB_CharlotteV3Voice'

def testGetVoice():
    voice = tts.get_voice(voiceModel).get_status_code()
    return voice

def speak(text):
    print(text)
    with open('./speech.wav', 'wb') as audio_file:
        res = tts.synthesize(text, accept='audio/wav', voice=voiceModel).get_result()
        audio_file.write(res.content)

    filename = 'speech.wav'
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done() 
