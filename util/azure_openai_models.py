from enum import Enum
from typing import final


@final
class AzureOpenAIModels(str, Enum):
    """
    Enum constants for the deployed Azure OpenAI models.
    """
    GPT_35T = "GPT-35-Turbo"
    GPT_4 = "GPT-4"
    GPT_4O = "GPT-4o"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.
        :return: A string representation of the object.
        """
        return f"{self.name}={self.value}"

    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        :return: A string representation of the object.
        """
        return self.value
