# logger.py
import inspect
import logging
import os
from pathlib import Path

from colorama import Fore, Style, init as colorama_init

from src.config import BASE_DIR, config

colorama_init(autoreset=True)

LOG_COLORS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA,
}

# Cache for loggers to avoid creating multiple loggers for the same module
_loggers = {}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = LOG_COLORS.get(record.levelname, "")
        message = super().format(record)
        return f"{log_color}{message}{Style.RESET_ALL}"


def get_logger(level=config.LOG_LEVEL):
    """
    Automatically create a logger based on the calling module's filename.

    Args:
        level: Logging level (optional, defaults to config.LOG_LEVEL)

    Returns:
        logging.Logger: Configured logger for the calling module
    """
    # Get the caller's frame
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename

    # Extract module name from filename
    module_name = Path(filename).stem

    # Use cached logger if it exists
    if module_name in _loggers:
        return _loggers[module_name]

    # Get log level (fallback to environment variable or default)
    if level is None:
        level = "INFO"

    # Create log file path relative to the project root
    logs_dir = os.path.join(BASE_DIR, "logs")
    log_file = os.path.join(logs_dir, f"{module_name}.log")

    # Ensure logs directory exists
    os.makedirs(logs_dir, exist_ok=True)

    formatter = ColoredFormatter(
        "[%(asctime)s] %(levelname)s [%(filename)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Individual log file handler
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(formatter)

    # Global log file handler
    global_handler = logging.FileHandler(
        os.path.join(logs_dir, "global.log"),
        encoding="utf-8",
    )
    global_handler.setFormatter(formatter)

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(global_handler)
    logger.addHandler(console)
    logger.propagate = False

    # Cache the logger
    _loggers[module_name] = logger

    return logger
