from enum import Enum
from typing import final


@final
class AzureSearchIndexes(str, Enum):
    """
    Constants for the supported Azure search indexes.
    """
    ARTILLERY_HELPER_CODE = "artillery-helper-code"
    TYPESCRIPT_API_HELPER_CODE = "typescript-api-helper-code"
    TYPESCRIPT_UI_HELPER_CODE = "typescript-ui-helper-code"

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
