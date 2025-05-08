import os

# Add references
from dotenv import load_dotenv
# from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage

def main():

    # Set the endpoint and model name
    endpoint = "https://ahmad-maf6qpkt-eastus2.openai.azure.com/openai/deployments/sofyan-gpt-4o"
    model_name = "sofyan-gpt-4o"

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    try:

        # Get configuration settings
        load_dotenv()
        endpoint = os.getenv("PROJECT_CONNECTION")
        model_name =  os.getenv("MODEL_DEPLOYMENT")
        API_KEY = os.getenv("API_KEY")

        # Initialize the project client
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(API_KEY),
        )

        ## Get the prompt from the user
        prompt = input("Enter your prompt: ")

        # Call the chat completion API
        response = client.complete(
            stream=True,
            messages=[
                SystemMessage(content="You are a helpful AI assistant that answers questions."),
                UserMessage(content=prompt)
            ],
            max_tokens=4096,
            temperature=1.0,
            top_p=1.0,
            model=model_name
        )

        # Print the response
        print("Response:")
        print("=====================================")
        
        for update in response:
            if update.choices:
                print(update.choices[0].delta.content or "", end="")

        client.close()


    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    main()
