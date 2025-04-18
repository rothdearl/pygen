import os
from enum import Enum
from typing import final

from definitions import SYSTEM_MESSAGES_DIR


@final
class SystemMessages(str, Enum):
    """
    Constants for the supported system messages.
    """
    ARTILLERY_DEV_MESSAGE = os.path.join(SYSTEM_MESSAGES_DIR, "artillery_dev_message.txt")
    CHAT_SUMMARY_MESSAGE = os.path.join(SYSTEM_MESSAGES_DIR, "chat_summary_message.txt")
    QA_MESSAGE = os.path.join(SYSTEM_MESSAGES_DIR, "qa_message.txt")
    TYPESCRIPT_API_DEV_MESSAGE = os.path.join(SYSTEM_MESSAGES_DIR, "typescript_api_dev_message.txt")
    TYPESCRIPT_UI_DEV_MESSAGE = os.path.join(SYSTEM_MESSAGES_DIR, "typescript_ui_dev_message.txt")

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
