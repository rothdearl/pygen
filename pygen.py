#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
from typing import Final, final

import requests
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai.lib.azure import AzureOpenAI
from requests.auth import HTTPBasicAuth

from definitions import ChatEntry, ChatHistory, OUTPUT_DIR
from util import AzureOpenAIChatCompletions, AzureOpenAIModels, AzureSearchIndex, AzureSearchIndexes
from util import ChatEntries, EnvVariables, Logger, SystemMessages

# Initialize the Azure OpenAI client.
API_VERSION: Final[str] = "2024-12-01-preview"
OPENAI_CLIENT: Final[AzureOpenAI] = AzureOpenAI(azure_endpoint=EnvVariables.AZURE_OPENAI_ENDPOINT,
                                                api_key=EnvVariables.AZURE_OPENAI_API_KEY, api_version=API_VERSION)

# Initialize the Search client.
SEARCH_CLIENT: Final[SearchClient] = SearchClient(endpoint=EnvVariables.AZURE_SEARCH_SERVICE_ENDPOINT,
                                                  index_name=AzureSearchIndexes.TYPESCRIPT_API_HELPER_CODE,
                                                  credential=AzureKeyCredential(EnvVariables.AZURE_SEARCH_KEY))

# Define the dev system message.
DEV_SYSTEM_MESSAGE: Final[str] = SystemMessages.TYPESCRIPT_API_DEV_MESSAGE


@final
class Globals:
    """
    Class for managing global constants and instances across the entire application.
    """
    VERSION: Final[str] = "1.3.1"
    options: argparse.Namespace


def get_jira_ticket_info(ticket_id: str) -> str:
    """
    Returns JIRA ticket information.
    :param ticket_id: The JIRA ticket id.
    :return: The JIRA ticket information.
    :raises RuntimeError: If an error occurs while retrieving the JIRA ticket or if there is no ticket information.
    """
    auth = HTTPBasicAuth(EnvVariables.JIRA_API_USERNAME, EnvVariables.JIRA_API_TOKEN)
    field = "description" if not Globals.options.field else Globals.options.field[0]
    url = f"{EnvVariables.JIRA_API_ENDPOINT}/{ticket_id}?fields={field}"

    # Get the JIRA ticket.
    Logger.info(f"Retrieving ticket information for '{ticket_id}' from field '{field}'...")
    response = requests.get(url=url, auth=auth)

    # If the request was successful, the status code will be 200.
    if response.status_code != 200:
        raise RuntimeError(f"Error retrieving JIRA ticket {ticket_id}. API response: {response.status_code}")
    else:
        data = response.json()

        if "fields" not in data:
            raise RuntimeError(f"JIRA ticket {ticket_id} does not contain the field '{field}'.")

        ticket_info = data["fields"][field]

    if not ticket_info:
        raise RuntimeError(f"No ticket information for '{ticket_id}' from field '{field}'")

    Logger.debug(f"Ticket information for '{ticket_id}':\n{ticket_info}")

    return ticket_info


def get_system_message_from_file(file_name: str) -> ChatEntry:
    """
    Returns a system message from a file.
    :param file_name: The file path.
    :return: A system message.
    """
    # Read in the content replacing all newlines with a space.
    with open(file_name, 'r') as file:
        content = file.read().replace("\n", " ").rstrip()

    return ChatEntries.as_system(content)


def initialize_logger() -> None:
    """
    Initializes the logger.
    :return: None
    """
    log_level = logging.NOTSET

    match Globals.options.log_level:
        case "debug":
            log_level = logging.DEBUG
        case "error":
            log_level = logging.ERROR
        case "info":
            log_level = logging.INFO
        case "warning":
            log_level = logging.WARNING

    # Initialize the logger.
    logging.basicConfig(format="%(message)s", level=log_level)

    # Set log levels for imported modules to ERROR.
    modules = ["azure", "httpcore", "httpx", "openai", "urllib3"]

    for module in modules:
        logging.getLogger(module).setLevel(logging.ERROR)


def main() -> None:
    """
    A program for generating test cases from JIRA tickets.
    :return: None
    """
    parse_arguments()
    initialize_logger()

    try:
        # Get the JIRA ticket id and information.
        ticket_id = Globals.options.ticket[0]
        ticket_info = get_jira_ticket_info(ticket_id)

        # Skip test cases?
        if Globals.options.no_test_cases:
            Logger.info("Skipping test case generation.")
            test_cases = ticket_info
        else:
            # Add the QA system message and the JIRA ticket information to the chat history.
            chat_history = [get_system_message_from_file(SystemMessages.QA_MESSAGE), ChatEntries.as_user(ticket_info)]

            # Generate test cases.
            test_cases = run_conversation_for_test_cases(chat_history)

        # Skip code?
        if Globals.options.no_code:
            Logger.info("Skipping code generation.")
            code = None
        else:
            helper_methods = search_for_helper_methods(test_cases)

            # Add the DEV system message, test cases and helper methods to the chat history.
            request = f"Generate code for the test cases.\nTest Cases: {test_cases}\nHelper Methods: {helper_methods}"
            chat_history = [get_system_message_from_file(DEV_SYSTEM_MESSAGE), ChatEntries.as_user(request)]

            # Generate code.
            code = run_conversation_for_code(chat_history)

        # Save the test cases and code.
        save_output(ticket_id, ticket_info, test_cases, code)
    except Exception as exception:
        Logger.error(f"error: {exception}")


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False,
                                     description="utility for generating test cases from jira tickets")
    generate = parser.add_mutually_exclusive_group()

    generate.add_argument("--no-code", action="store_true", help="do not generate code")
    generate.add_argument("--no-test-cases", action="store_true", help="do not generate test cases")
    parser.add_argument("-H", "--helper-methods", help="the number of helper methods to query for", metavar="methods",
                        nargs=1, type=int)
    parser.add_argument("-f", "--field", help="the jira ticket qa field", metavar="field", nargs=1)
    parser.add_argument("-l", "--log-level", choices=["debug", "info", "warning", "error"], default="info",
                        help="set the log level")
    parser.add_argument("-m", "--model", help="the model to use for generating code", metavar="model", nargs=1)
    parser.add_argument("-o", "--output-folder", help="the output folder", metavar="folder", nargs=1)
    parser.add_argument("-s", "--split", action="store_true", help="split test cases and code into separate files")
    parser.add_argument("-t", "--ticket", help="the jira ticket id", metavar="ticket", nargs=1, required=True)
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {Globals.VERSION}")

    # Parse the arguments.
    Globals.options = parser.parse_args()


def run_conversation_for_code(chat_history: ChatHistory) -> str:
    """
    Calls the chat completions API for generating code.
    :param chat_history: The chat history.
    :return: The response message and chat history.
    """
    model = AzureOpenAIModels.GPT_4 if not Globals.options.model else Globals.options.model[0]

    Logger.info(f"Generating code with model '{model}'...")
    Logger.debug(f"Calling the chat completions API for code with:\n{json.dumps(chat_history)}")
    code = AzureOpenAIChatCompletions.run_conversation(OPENAI_CLIENT, model=model, chat_history=chat_history,
                                                       temperature=0.2, top_p=0.1).content
    Logger.debug(f"Chat completions response:\n{code}\n")
    Logger.info("Code generation complete.")

    return code


def run_conversation_for_test_cases(chat_history: ChatHistory) -> str:
    """
    Calls the chat completions API for generating test cases.
    :param chat_history: The chat history.
    :return: The response content and the updated chat history.
    """
    model = AzureOpenAIModels.GPT_35T

    Logger.info(f"Generating test cases with model '{model}'...")
    Logger.debug(f"Calling the chat completions API for test cases with:\n{json.dumps(chat_history)}")
    test_cases = AzureOpenAIChatCompletions.run_conversation(OPENAI_CLIENT, model=model,
                                                             chat_history=chat_history).content
    Logger.debug(f"Chat completions response:\n{test_cases}\n")
    Logger.info("Test case generation complete.")

    return test_cases


def save_output(jira_ticket: str, ticket_info: str, test_cases: str, code: str) -> None:
    """
    Saves the AI generated test cases and code to file.
    :param jira_ticket: The JIRA ticket number.
    :param ticket_info: The JIRA ticket information.
    :param test_cases: The test cases.
    :param code: The code.
    :return: None
    """
    encoding = "utf-8"
    output_dir = OUTPUT_DIR if not Globals.options.output_folder else Globals.options.output[0]
    output_file_path = os.path.join(output_dir, jira_ticket.lower())
    output_file_test_cases = f"{output_file_path}-test-cases.txt"

    # Write the test information.
    with open(output_file_test_cases, encoding=encoding, mode="w") as text_file:
        text_file.write(f"{jira_ticket}:\n---------\n{ticket_info}\n")

    # Test cases generated?
    if not Globals.options.no_test_cases:
        with open(output_file_test_cases, encoding=encoding, mode="a") as text_file:
            text_file.write(f"\nTest Cases:\n-----------\n{test_cases}\n")

        Logger.info(f"Test cases for {jira_ticket} saved to '{output_file_test_cases}'")
    else:
        Logger.info(f"Test information for {jira_ticket} saved to '{output_file_test_cases}'")

    # Code generated?
    if not Globals.options.no_code:
        # Split test cases and code into separate files?
        if Globals.options.split:
            output_file_code = f"{output_file_path}-code.test.ts"

            # Trim the first and last non-compiling lines.
            code = code.replace("```typescript\n", "")
            code = code.replace("```", "")

            # Write the code.
            with open(output_file_code, encoding=encoding, mode="w") as text_file:
                text_file.write(code)

            Logger.info(f"Code for {jira_ticket} saved to '{output_file_code}'")
        else:
            with open(output_file_test_cases, encoding=encoding, mode="a") as text_file:
                text_file.write(f"\nCode:\n-----\n{code}\n")

            Logger.info(f"Code for {jira_ticket} saved to '{output_file_test_cases}'")


def search_for_helper_methods(test_cases: str) -> str:
    """
    Searches the indexed code for helper methods.
    :param test_cases: The test cases to query.
    :return: The helper methods.
    """
    helper_methods = []
    top_results = 5 if not Globals.options.helper_methods else Globals.options.helper_methods[0]

    Logger.info(f"Searching for the top {top_results} helper methods...")

    for result in AzureSearchIndex.do_hybrid_search(OPENAI_CLIENT, SEARCH_CLIENT, query=test_cases,
                                                    top_results=top_results):
        helper_methods.extend(method for method in result)

    helper_methods = "\n".join(helper_methods)
    Logger.debug(f"Search response:\n{helper_methods}")
    Logger.info("Search complete.")

    return helper_methods


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass  # Process interrupted; exit quietly.
