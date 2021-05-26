from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator = IAMAuthenticator('U4wnjJDAcQ_-emDRWxfazc3PpGpCOJtxuSoQxdg0jHZp') # replace with API key
assistant_id = '8e3a8f71-d22c-4a92-a2d1-90dc1395ffc3' # replace with assistant ID

def getChatbotResponse(user_input,context):
    # Create Assistant service object.
    assistant = AssistantV2(
        version = '2020-09-24',
        authenticator = authenticator
    )
    assistant.set_service_url('https://api.eu-gb.assistant.watson.cloud.ibm.com/')

    print(user_input)
    # Start conversation with empty message.
    response = assistant.message_stateless(
        assistant_id,
        input = {"text": user_input},
        context = context
    ).get_result()
    print(response)
    # Print the output from dialog, if any. Supports only a single
    # text response.
    return response['output']['generic'], response['context']
    if response['output']['generic']:
        if response['output']['generic'][0]['response_type'] == 'text':
            print(response['output']['generic'][0]['text'])