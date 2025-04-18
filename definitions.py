import os
from typing import Any, Final

# Define directory paths.
_CURRENT_DIR: Final[str] = os.path.dirname(__file__)
METADATA_DIR: Final[str] = os.path.join(_CURRENT_DIR, "metadata")
OUTPUT_DIR: Final[str] = os.path.join(_CURRENT_DIR, "ai_generated")
PROJECT_ROOT_DIR: Final[str] = _CURRENT_DIR
SYSTEM_MESSAGES_DIR: Final[str] = os.path.join(_CURRENT_DIR, "system_messages")

# Define OS constants.
OS_IS_POSIX: Final[bool] = os.name == "posix"
OS_IS_WINDOWS: Final[bool] = os.name == "nt"

# Define type aliases.
ChatEntry = dict[str, str]
ChatHistory = list[ChatEntry]
ChatTool = dict[str, Any]
Embeddings = list[float]
SearchIndexResults = list[tuple[str, str, str]]
