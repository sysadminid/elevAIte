import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from flight_booking_plugin import FlightBookingPlugin
from typing import Awaitable, Callable
from semantic_kernel.filters import FunctionInvocationContext
from semantic_kernel.functions.function_result import FunctionResult


def has_user_permission(plugin_name: str, function_name: str) -> bool:
    if plugin_name == "flight_booking_plugin" and function_name == "book_flight":
        print("System Message: The agent requires an approval to complete this operation. Do you approve (Y/N)")
        should_proceed = input("User: ").strip().upper()

        if should_proceed != "Y":
            return False

    return True

# Create the function filer class
async def permission_filter(context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]]) -> None:

    # Implement the function invocation method
    if not has_user_permission(context.function.plugin_name, context.function.name):
        context.result = FunctionResult(
            function=context.function.metadata,
            value="The operation was not approved by the user. Tell the user with sorry words.",
            rendered_prompt=None,
            metadata={
                "name": context.function.metadata.name,
                "plugin_name": context.function.plugin_name,
                "description": context.function.metadata.description
                },
        )
        return

    await next(context)


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
    kernel.add_plugin(FlightBookingPlugin(), "flight_booking_plugin")

    # Add the permission filter to the kernel
    kernel.add_filter('function_invocation', permission_filter)

    settings = AzureChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
    )

    chat_history = ChatHistory()

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

    chat_history.add_system_message("Assume the current date is January 1 2025")
    add_user_message("Find me a flight to Tokyo on January 19")
    await get_reply()
    get_input()
    await get_reply()

if __name__ == "__main__":
        asyncio.run(main())
