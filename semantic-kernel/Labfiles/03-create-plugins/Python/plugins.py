import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions.kernel_arguments import KernelArguments
from flight_booking_plugin import FlightBookingPlugin
#from flight_booking_plugin import SearchFlightPlugin, BookFlightPlugin


async def main():

    load_dotenv()
    # Set your values in the .env file
    api_key = os.getenv("PROJECT_KEY")
    endpoint = os.getenv("PROJECT_ENDPOINT")
    deployment_name = os.getenv("DEPLOYMENT_NAME")

    kernel = Kernel()
    chat_completion = AzureChatCompletion(
        api_key=api_key,
        endpoint=endpoint,
        deployment_name=deployment_name
    )
    kernel.add_service(chat_completion)

    # Add the plugin to the kernel
    kernel.add_plugin(FlightBookingPlugin(), "flight_booking_plugin")

    # Configure the function choice behavior
    settings = AzureChatPromptExecutionSettings(
        service_id="chat",
        max_tokens=2000,
        temperature=0.7,
        top_p=0.8,
        function_choice_behavior=FunctionChoiceBehavior.Required(filters={"included_functions": ["flight_booking_plugin-search_flights"]}),
    )

    # settings = AzureChatPromptExecutionSettings(
    #     function_choice_behavior=FunctionChoiceBehavior.Auto(),
    # )

    chat_history = ChatHistory()
    chat_history.add_system_message("The year is 2025 and the current month is January")

    async def get_reply():
        reply = await chat_completion.get_chat_message_content(
            chat_history=chat_history,
            kernel=kernel,
            settings=settings
        )
        print("Assistant:", reply)
        chat_history.add_assistant_message(str(reply))

    def get_input():
        user_input = input("User: ")
        if user_input.strip() != "":
            chat_history.add_user_message(user_input)
        return user_input

    def add_user_message(msg: str):
        print(f"User: {msg}")
        chat_history.add_user_message(msg)

    chat_history.add_system_message("You are a flight booking assistant. You can search for flights but not book them.")
    chat_history.add_user_message("Find me a flight to Tokyo on the 19")
    await get_reply()
    get_input()
    await get_reply()

if __name__ == "__main__":
        asyncio.run(main())
