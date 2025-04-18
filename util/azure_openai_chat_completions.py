import json
from typing import final, Callable

from openai.lib.azure import AzureOpenAI
from openai.types.chat import ChatCompletionMessage

from definitions import ChatHistory, ChatTool


@final
class AzureOpenAIChatCompletions:
    """
    Utility class for the Azure OpenAI chat completions.
    """

    @staticmethod
    def append_tool_responses(client: AzureOpenAI, *, model: str, chat_history: ChatHistory, tools: list[ChatTool],
                              function_names: list[str], functions: list[Callable]) -> ChatHistory:
        """
        Appends the responses from calling the tools to the chat history.
        :param client: The Azure OpenAI client.
        :param model: The model to use.
        :param chat_history: The chat history.
        :param tools: The chat completion tools.
        :param function_names: The list of function names to map to the functions.
        :param functions: The list of functions to map to the function names.
        :return: The chat history.
        """
        from util import ChatEntries  # Avoid circular import.

        response = client.chat.completions.create(model=model, messages=chat_history, tools=tools, tool_choice="auto")
        tools = response.choices[0].message

        # Map function names to actual functions.
        available_tools = {key: value for key, value in zip(function_names, functions)}

        # Process each tool call.
        for tool_call in tools.tool_calls:
            tool_to_call = available_tools.get(tool_call.function.name)

            # Deserialize the JSON string into arguments.
            tool_args = json.loads(tool_call.function.arguments)

            # Call the function and append the response to the messages.
            tool_response = tool_to_call(**tool_args)
            chat_history.append(ChatEntries.as_system(tool_response))

        return chat_history

    @staticmethod
    def run_conversation(client: AzureOpenAI, *, model: str, chat_history: ChatHistory, temperature: float = 1,
                         top_p: float = 1) -> ChatCompletionMessage:
        """
        Runs a conversation with the chat completions AI and returns the response.
        :param client: The Azure OpenAI client.
        :param model: The model to use.
        :param chat_history: The chat history.
        :param temperature: The sampling temperature. The default value is 1.
        :param top_p: The nucleus sampling. The default value is 1.
        :return: The AI response.
        """
        response = client.chat.completions.create(model=model, messages=chat_history, temperature=temperature,
                                                  top_p=top_p)

        return response.choices[0].message
