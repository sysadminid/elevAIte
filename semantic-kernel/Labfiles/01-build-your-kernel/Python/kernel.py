import os
import asyncio
from dotenv import load_dotenv

# Import namespaces
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions.kernel_arguments import KernelArguments


async def main():

    load_dotenv()
    # Set your values in the .env file
    api_key = os.getenv("PROJECT_KEY")
    endpoint = os.getenv("PROJECT_ENDPOINT")
    deployment_name = os.getenv("DEPLOYMENT_NAME")


    # Create a kernel with Azure OpenAI chat completion
    kernel = Kernel()
    chat_completion = AzureChatCompletion(
        api_key=api_key,
        endpoint=endpoint,
        deployment_name=deployment_name
    )
    kernel.add_service(chat_completion)


    # Test the chat completion service
    response = await kernel.invoke_prompt(
        "Give me a list of 10 breakfast foods with eggs and oats",
        KernelArguments())
    print("Assistant > \n\n" + str(response))


if __name__ == "__main__":
        asyncio.run(main())
