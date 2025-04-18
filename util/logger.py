import logging
from datetime import datetime
from typing import final

from definitions import OS_IS_WINDOWS
from util import ConsoleColors as Colors

# Fix ANSI escape sequences on Windows.
if OS_IS_WINDOWS:
    from colorama import just_fix_windows_console

    just_fix_windows_console()


@final
class Logger:
    """
    Utility class for logging.
    """

    @staticmethod
    def _color_current_time() -> str:
        """
        Adds color to the current time.
        :return: The current time.
        """
        date_format = "%Y-%m-%d %H:%M:%S,%f"
        now = datetime.now().strftime(date_format)[:-3]  # Truncate the microseconds to milliseconds.

        return f"{Colors.DIM}{now}{Colors.RESET}"

    @staticmethod
    def _color_log_level(log_level: int) -> str:
        """
        Adds color to the log level.
        :param log_level: The log level.
        :return: The log level.
        """
        left_bracket = f"{Colors.DIM}{Colors.BOLD}[{Colors.RESET}"
        right_bracket = f"{Colors.DIM}{Colors.BOLD}]{Colors.RESET}"
        level_name = logging.getLevelName(log_level)

        match log_level:
            case logging.DEBUG:
                level_name = f"{Colors.YELLOW}{level_name}{Colors.RESET}"
            case logging.ERROR:
                level_name = f"{Colors.BLINK}{Colors.BRIGHT_RED}{level_name}{Colors.RESET}"
            case logging.INFO:
                level_name = f"{Colors.BRIGHT_BLUE}{level_name}{Colors.RESET}"
            case logging.WARNING:
                level_name = f"{Colors.BRIGHT_YELLOW}{level_name}{Colors.RESET}"

        return f"{left_bracket}{level_name}{right_bracket}"

    @staticmethod
    def _color_message(log_level: int, message: str) -> str:
        """
        Adds color to the message.
        :param log_level: The log level.
        :param message: The message.
        :return: The message.
        """
        match log_level:
            case logging.DEBUG:
                message = f"{Colors.DIM}{message}{Colors.RESET}"
            case logging.ERROR:
                message = f"{Colors.BG_RED}{message}{Colors.RESET}"
            case logging.WARNING:
                message = f"{Colors.BOLD}{Colors.DIM}{message}{Colors.RESET}"

        return message

    @staticmethod
    def _log_message(*, log_level: int, message: str) -> None:
        """
        Logs the message.
        :param log_level: The log level.
        :param message: The message.
        :return: None
        """
        current_time = Logger._color_current_time()
        double_right_arrow = f"{Colors.CYAN}»{Colors.RESET}"
        level = Logger._color_log_level(log_level)
        message = Logger._color_message(log_level, message)
        right_arrow = f"{Colors.BRIGHT_GREEN}➡{Colors.RESET}"

        logging.log(level=log_level, msg=f"{right_arrow} {current_time} {level} {double_right_arrow} {message}")

    @staticmethod
    def debug(message: str) -> None:
        """
        Logs the message.
        :param message: The message.
        :return: None
        """
        Logger._log_message(log_level=logging.DEBUG, message=message)

    @staticmethod
    def error(message: str) -> None:
        """
        Logs the message.
        :param message: The message.
        :return: None
        """
        Logger._log_message(log_level=logging.ERROR, message=message)

    @staticmethod
    def info(message: str) -> None:
        """
        Logs the message.
        :param message: The message.
        :return: None
        """
        Logger._log_message(log_level=logging.INFO, message=message)

    @staticmethod
    def warning(message: str) -> None:
        """
        Logs the message.
        :param message: The message.
        :return: None
        """
        Logger._log_message(log_level=logging.WARNING, message=message)
