from enum import Enum
from typing import final


@final
class MetadataFiles(str, Enum):
    """
    Constants for the supported metadata files.
    """
    TYPESCRIPT_API_HELPER_CODE = "typescript_api_helper_code.ts"
    TYPESCRIPT_UI_HELPER_CODE = "typescript_ui_helper_code.ts"

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
