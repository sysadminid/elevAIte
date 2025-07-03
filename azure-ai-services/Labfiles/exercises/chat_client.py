# from azure.ai.projects import AIProjectClient
# from azure.identity import DefaultAzureCredential
# from azure.ai.inference.models import SystemMessage, UserMessage

# try:

#     # Initialize the project client
#     project_connection_string = "eastus.api.azureml.ms;e032d7bd-deba-452a-aff4-acd44e3c4d96;mslearn-resource-group;ahmadsofyan-0888"
#     project_client = AIProjectClient.from_connection_string(
#         credential=DefaultAzureCredential(),
#         conn_str=project_connection_string,
#     )

#     ## Get a chat client
#     chat = project_client.inference.get_chat_completions_client()

#     # Get a chat completion based on a user-provided prompt
#     user_prompt = input("Enter a question: ")

#     response = chat.complete(
#         model="sofyan-gpt-4o",
#         messages=[
#             SystemMessage("You are a helpful AI assistant that answers questions."),
#             UserMessage(user_prompt)
#             ],
#         )
#     print(response.choices[0].message.content)

# except Exception as ex:
#     print(ex)


from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import openai


try:
    # Initialize the project client
    project_connection_string = "eastus.api.azureml.ms;e032d7bd-deba-452a-aff4-acd44e3c4d96;mslearn-resource-group;ahmadsofyan-0888"
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=project_connection_string,
    )

    ## Get an Azure OpenAI chat client
    openai_client = project_client.inference.get_azure_openai_client(api_version="2024-06-01")

    # Get a chat completion based on a user-provided prompt
    user_prompt = input("Enter a question:")
    response = openai_client.chat.completions.create(
        model="gpt-4-model",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant that answers questions."},
            {"role": "user", "content": user_prompt},
        ]
    )
    print(response.choices[0].message.content)

except Exception as ex:
    print(ex)
