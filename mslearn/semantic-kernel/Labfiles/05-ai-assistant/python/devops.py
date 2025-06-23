import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.prompt_template.handlebars_prompt_template import HandlebarsPromptTemplate
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig, InputVariable
from typing import Awaitable, Callable
from semantic_kernel.filters import FunctionInvocationContext
from semantic_kernel.functions import FunctionResult
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from pathlib import Path

async def main():

    load_dotenv()
    api_key = os.getenv("PROJECT_KEY")
    endpoint = os.getenv("PROJECT_ENDPOINT")
    deployment_name = os.getenv("DEPLOYMENT_NAME")

    # Create a kernel builder with Azure OpenAI chat completion
    kernel = Kernel()
    chat_completion = AzureChatCompletion(
        api_key=api_key,
        endpoint=endpoint,
        deployment_name=deployment_name
    )
    kernel.add_service(chat_completion)

    # Import plugins to the kernel
    kernel.add_plugin(DevopsPlugin(), plugin_name="DevopsPlugin")

    # Add filters to the kernel
    kernel.add_filter('function_invocation', permission_filter)

    # Create a kernel function to deploy the staging environment
    deploy_stage_function = KernelFunctionFromPrompt(
        prompt="""This is the most recent build log:


        If there are errors, do not deploy the stage environment. Otherwise, invoke the stage deployment function""",
        function_name="DeployStageEnvironment",
        description="Deploy the staging environment"
    )

    kernel.add_function(plugin_name="DeployStageEnvironment", function=deploy_stage_function)

    # Create a handlebars prompt
    hb_prompt = """<message role="system">Instructions: Before creating a new branch for a user, request the new branch name and base branch name/message>
        <message role="user">Can you create a new branch?</message>
        <message role="assistant">Sure, what would you like to name your branch? And which base branch would you like to use?</message>
        <message role="user"></message>
        <message role="assistant">"""

    # Create the prompt template config using handlebars format
    hb_template = HandlebarsPromptTemplate(
        prompt_template_config=PromptTemplateConfig(
            template=hb_prompt,
            template_format="handlebars",
            name="CreateBranch",
            description="Creates a new branch for the user",
            input_variables=[
                InputVariable(name="input", description="The user input", is_required=True)
            ]
        ),
        allow_dangerously_set_content=True,
    )

    # Create a plugin function from the prompt
    prompt_function = KernelFunctionFromPrompt(
        function_name="CreateBranch",
        description="Creates a branch for the user",
        template_format="handlebars",
        prompt_template=hb_template,
    )
    kernel.add_function(plugin_name="BranchPlugin", function=prompt_function)

    # Create prompt execution settings
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create chat history
    chat_history = ChatHistory()

    # User interaction logic
    async def get_reply():
        reply = await chat_completion.get_chat_message_content(
            chat_history=chat_history,
            kernel=kernel,
            settings=execution_settings
        )
        print("Assistant:", reply)
        chat_history.add_assistant_message(str(reply))

    def get_input():
        user_input = input("User: ")
        if user_input.strip() != "":
            chat_history.add_user_message(user_input)
        return user_input

    print("Press enter to exit")
    print("Assistant: How may I help you?")
    user_input = input("User: ")

    if user_input.strip() != "":
        chat_history.add_user_message(user_input)

    while user_input.strip() != "":
        await get_reply()
        user_input = get_input()


# A class for Devops functions
class DevopsPlugin:
    """A plugin that performs developer operation tasks."""

    # Create a kernel function to build the stage environment
    @kernel_function(name="BuildStageEnvironment")
    def build_stage_environment(self):
        return "Stage build completed."

    @kernel_function(name="DeployToStage")
    def deploy_to_stage(self):
        return "Staging site deployed successfully."

    @kernel_function(name="DeployToProd")
    def deploy_to_prod(self):
        return "Production site deployed successfully."

    @kernel_function(name="CreateNewBranch")
    def create_new_branch(self, branchName: str, baseBranch: str):
        return f"Created new branch `{branchName}` from `{baseBranch}`."

    @kernel_function(name="CreateNewBranch")
    def create_new_branch(self, branchName: str, baseBranch: str):
        return f"Created new branch `{branchName}` from `{baseBranch}`."

    @kernel_function(name="ReadLogFile")
    def read_log_file(self):
        file_path = Path(__file__) / "Files"
        with open("Files/build.log", 'r', encoding='utf-8') as file:
            return file.read()

# Create a function filter
async def permission_filter(context: FunctionInvocationContext, next: Callable[[FunctionInvocationContext], Awaitable[None]]) -> None:
    await next(context)
    result = context.result

    # Check the plugin and function names
    if context.function.plugin_name == "DevopsPlugin" and context.function.name == "DeployToProd":
        # Request user approval
        print("System Message: The assistant requires approval to complete this operation. Do you approve (Y/N)")
        should_proceed = input("User: ").strip()

        # Proceed if approved
        if should_proceed.upper() != "Y":
            context.result = FunctionResult(
                function=result.function,
                value="The operation was not approved by the user",
            )


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
