from typing import final

from definitions import ChatEntry


@final
class ChatEntries:
    """
    Utility class for chat entries.
    """

    @staticmethod
    def _get_chat_entry(role: str, content: str) -> ChatEntry:
        """
        Returns a chat entry.
        :param role: The role.
        :param content: The content.
        :return: A chat entry.
        """
        return {"role": role, "content": content}

    @staticmethod
    def as_assistant(content: str) -> ChatEntry:
        """
        Returns a chat entry for the assistant role.
        :param content: The content.
        :return: A chat entry.
        """
        return ChatEntries._get_chat_entry("assistant", content)

    @staticmethod
    def as_system(content: str) -> ChatEntry:
        """
        Returns a chat entry for the system role.
        :param content: The content.
        :return: A chat entry.
        """
        return ChatEntries._get_chat_entry("system", content)

    @staticmethod
    def as_user(content: str) -> ChatEntry:
        """
        Returns a chat entry for the user role.
        :param content: The content.
        :return: A chat entry.
        """
        return ChatEntries._get_chat_entry("user", content)
