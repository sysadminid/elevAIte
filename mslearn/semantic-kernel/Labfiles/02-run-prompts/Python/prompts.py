import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.contents.text_content import TextContent
from semantic_kernel.prompt_template import KernelPromptTemplate, HandlebarsPromptTemplate, PromptTemplateConfig

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


    # Create the chat history
    chat_history = ChatHistory()


    async def get_reply():
        # Get the reply from the chat completion service
        reply = await chat_completion.get_chat_message_content(
            chat_history=chat_history,
            kernel=kernel,
            settings=AzureChatPromptExecutionSettings()
        )
        print("Assistant:", reply)
        chat_history.add_assistant_message(str(reply))

    # Create a semantic kernel prompt template
    sk_prompt_template = KernelPromptTemplate(
        prompt_template_config=PromptTemplateConfig(
            template="""
            You are a helpful career advisor. Based on the users's skills and interest, suggest up to 5 suitable roles.
            Return the output as JSON in the following format:
            "Role Recommendations":
            {
            "recommendedRoles": [],
            "industries": [],
            "estimatedSalaryRange": ""
            }

            My skills are: {{$skills}} My interests are: {{$interests}} What are some roles that would be suitable for me?
            """,
            name="recommend_roles_prompt",
            template_format="semantic-kernel",
        )
    )


    # Render the Semantic Kernel prompt with arguments
    sk_rendered_prompt = await sk_prompt_template.render(
        kernel,
        KernelArguments(
            skills="Software Engineering, C#, Python, Drawing, Guitar, Dance",
            interests="Education, Psychology, Programming, Helping Others"
        )
    )


    # Add the Semantic Kernel prompt to the chat history and get the reply
    chat_history.add_user_message(sk_rendered_prompt)
    await get_reply()


    # Create a handlebars template for analyzing skill gaps
    hb_prompt_template = HandlebarsPromptTemplate(
        prompt_template_config=PromptTemplateConfig(
            template="""
            <message role="system">
            Instructions: You are a career advisor. Analyze the skill gap between
            the user's current skills and the requirements of the target role.
            </message>
            <message role="user">Target Role: {{targetRole}}</message>
            <message role="user">Current Skills: {{currentSkills}}</message>

            <message role="assistant">
            "Skill Gap Analysis":
            {
                "missingSkills": [],
                "coursesToTake": [],
                "certificationSuggestions": []
            }
            </message>
            """,
            name="missing_skills_prompt",
            template_format="handlebars",
        )
    )

    # Create a handlebars template for estimating skills acquisition time
    hb_prompt_template_acquisition = HandlebarsPromptTemplate(
        prompt_template_config=PromptTemplateConfig(
            template="""
            <message role="system">
            Instructions: You are a career advisor. Estimate the time required to acquire the skills needed for the target role based
            on the user's current skills, missing skills, course to take, and certification suggestions.
            </message>
            <message role="user">Follow up: {{user_follow_up}}</message>

            <message role="assistant">
            "Skill Acquisition Estimate":
            {
                "estimatedTime": {},
                "totalEstimatedTime": ""
            }
            """,
            name="estimate_skills_acquisition_prompt",
            template_format="handlebars",
        )
    )


    # Render the Handlebars prompt with arguments for skill gap analysis
    hb_rendered_prompt = await hb_prompt_template.render(
        kernel,
        KernelArguments(
            targetRole="Game Developer",
            currentSkills="Software Engineering, C#, Python, Drawing, Guitar, Dance"
        )
    )


    # Add the Handlebars prompt to the chat history and get the reply
    chat_history.add_user_message(hb_rendered_prompt)
    await get_reply()


    # Get a follow-up prompt from the user
    print("Assistant: How can I help you?")
    user_input = input("User: ")


    # Render the Handlebars prompt with arguments for estimating skills acquisition time
    hb_rendered_acquisition_prompt = await hb_prompt_template_acquisition.render(
        kernel,
        KernelArguments(
            user_follow_up=user_input
        )
    )


    # Add the Handlebars prompt to the chat history and get the reply
    chat_history.add_user_message(hb_rendered_acquisition_prompt)
    await get_reply()


    # # Add the user input to the chat history and get the reply
    # chat_history.add_user_message(user_input)
    # await get_reply()

    # Print the chat history
    last_message = chat_history[-1]
    print(f"\nLast Chat History: {chat_history[-1]}")
    print(f"{last_message.role}:")
    for item in last_message.items:
        if isinstance(item, TextContent):
            print(f"  Text: {item.text}")

    # Print the chat history
    print("\nFull Chat History:\n")
    for message in chat_history:
        print(f"{message.role}:")
        for item in message.items:
            if isinstance(item, TextContent):
                print(f"  Text: {item.text}\n\n")



if __name__ == "__main__":
        asyncio.run(main())
