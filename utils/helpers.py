import os
from datetime import datetime
from typing import Optional, List, Union

from core.logger import log_info, log_error


def clean_query(query: Optional[str]) -> Optional[str]:
    """
    Removes extra spaces and converts to lowercase. Useful for normalizing voice commands.
    """
    try:
        if query is not None:
            return query.strip().lower()
        return None
    except Exception as e:
        log_error(f"Error cleaning query: {e}")
        return None


def check_file_exists(file_path: str) -> bool:
    """Checks if the given file exists. Returns True or False."""
    try:
        return os.path.isfile(file_path)
    except Exception as e:
        log_error(f"Error checking file: {e}")
        return False


def check_folder_exists(folder_path: str) -> bool:
    """Checks if the given folder exists. Returns True or False."""
    try:
        return os.path.isdir(folder_path)
    except Exception as e:
        log_error(f"Error checking folder: {e}")
        return False


def get_file_size(file_path: str) -> Optional[float]:
    """
    Returns the size of a file in MB. Returns None if file doesn't exist.
    """
    try:
        if check_file_exists(file_path):
            size_bytes = os.path.getsize(file_path)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            return size_mb
        return None
    except Exception as e:
        log_error(f"Error getting file size: {e}")
        return None


def get_folder_size(folder_path: str) -> Optional[float]:
    """
    Recursively calculates the total size of a folder in MB.
    """
    try:
        total_size = 0
        for dirpath, _, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except OSError:
                        # Skip files that cannot be accessed
                        pass
        return round(total_size / (1024 * 1024), 2)
    except Exception as e:
        log_error(f"Error getting folder size: {e}")
        return None


def get_current_time(format_str: str = "%H:%M:%S") -> Optional[str]:
    """Returns current time formatted as desired. Default HH:MM:SS."""
    try:
        return datetime.now().strftime(format_str)
    except Exception as e:
        log_error(f"Error getting current time: {e}")
        return None


def get_current_date(format_str: str = "%Y-%m-%d") -> Optional[str]:
    """Returns current date formatted as desired. Default YYYY-MM-DD."""
    try:
        return datetime.now().strftime(format_str)
    except Exception as e:
        log_error(f"Error getting current date: {e}")
        return None


def contains_keyword(text: str, keywords: Union[str, List[str]]) -> bool:
    """
    Checks if any of the given keywords are in the text. Useful for command matching.
    """
    try:
        if not isinstance(text, str):
            return False
        lower_text = text.lower()

        if isinstance(keywords, str):
            return keywords.lower() in lower_text

        if isinstance(keywords, list):
            return any((isinstance(kw, str) and kw.lower() in lower_text) for kw in keywords)

        return False
    except Exception as e:
        log_error(f"Error checking keyword match: {e}")
        return False
