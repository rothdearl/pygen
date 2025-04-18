from enum import Enum
from typing import final

from util import AzureSearchIndexes


@final
class AzureSearchSemanticConfigs(str, Enum):
    """
    Constants for the supported Azure search semantic configurations.
    """
    ARTILLERY_HELPER_CODE = f"{AzureSearchIndexes.ARTILLERY_HELPER_CODE}-semantic-config"
    TYPESCRIPT_API_HELPER_CODE = f"{AzureSearchIndexes.TYPESCRIPT_API_HELPER_CODE}-semantic-config"
    TYPESCRIPT_UI_HELPER_CODE = f"{AzureSearchIndexes.TYPESCRIPT_UI_HELPER_CODE}-semantic-config"

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
