import os
from typing import Final, final

from dotenv import load_dotenv

# Load environment variables.
load_dotenv()


@final
class EnvVariables:
    """
    Constants for the environment variables.
    """
    AZURE_OPENAI_API_KEY: Final[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Final[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_SEARCH_KEY: Final[str] = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_SERVICE_ENDPOINT: Final[str] = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    JIRA_API_ENDPOINT: Final[str] = os.getenv("JIRA_API_ENDPOINT")
    JIRA_API_TOKEN: Final[str] = os.getenv("JIRA_API_TOKEN")
    JIRA_API_USERNAME: Final[str] = os.getenv("JIRA_API_USERNAME")
