import os
from urllib.request import urlopen, Request
import base64

# Add references
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import (
    SystemMessage,
    UserMessage,
    TextContentItem,
    AudioContentItem,
    InputAudio,
    AudioContentFormat,
)

def main():

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    try:

        # Get configuration settings
        load_dotenv()
        project_connection = os.getenv("PROJECT_CONNECTION")
        model_deployment =  os.getenv("MODEL_DEPLOYMENT")

        # Initialize the project client
        project_client = AIProjectClient.from_connection_string(
           conn_str=project_connection,
           credential=DefaultAzureCredential())


        ## Get a chat client
        chat_client = project_client.inference.get_chat_completions_client(model=model_deployment)


        # Initialize prompts
        system_message = "You are an AI assistent in a grocery store that sells fruit."
        prompt = ""

        # Loop until the user types 'quit'
        while True:
            prompt = input("\nAsk a question about the audio\n(or type 'quit' to exit)\n")
            if prompt.lower() == "quit":
                break
            elif len(prompt) == 0:
                    print("Please enter a question.\n")
            else:
                print("Getting a response ...\n")


                # Get a response to audio input
                # file_path = "https://github.com/microsoftlearning/mslearn-ai-language/raw/refs/heads/main/labfiles/09-audio-chat/data/manzanas.mp3"
                file_path = "https://github.com/microsoftlearning/mslearn-ai-language/raw/refs/heads/main/labfiles/09-audio-chat/data/caomei.mp3"
                response = chat_client.complete(
                    messages=[
                        SystemMessage(system_message),
                        UserMessage(
                            [
                                TextContentItem(text=prompt),
                                {
                                    "type": "audio_url",
                                    "audio_url": {"url": file_path}
                                }
                            ]
                        )
                    ]
                )
                print(response.choices[0].message.content)


    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
