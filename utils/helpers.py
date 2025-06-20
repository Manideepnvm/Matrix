# utils/helpers.py

import os
import logging
from datetime import datetime
from core.logger import log_info, log_error

def clean_query(query):
    """
    Removes extra spaces and converts to lowercase.
    Useful for normalizing voice commands.
    """
    try:
        if query:
            return query.strip().lower()
        return ""
    except Exception as e:
        log_error(f"Error cleaning query: {e}")
        return ""

def check_file_exists(filepath):
    """
    Checks if the given file exists.
    Returns True or False.
    """
    try:
        return os.path.isfile(filepath)
    except Exception as e:
        log_error(f"Error checking file: {e}")
        return False

def check_folder_exists(folderpath):
    """
    Checks if the given folder exists.
    Returns True or False.
    """
    try:
        return os.path.isdir(folderpath)
    except Exception as e:
        log_error(f"Error checking folder: {e}")
        return False

def get_file_size(filepath):
    """
    Returns the size of a file in MB.
    Returns None if file doesn't exist.
    """
    try:
        if check_file_exists(filepath):
            size_bytes = os.path.getsize(filepath)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            return size_mb
        return None
    except Exception as e:
        log_error(f"Error getting file size: {e}")
        return None

def get_folder_size(folderpath):
    """
    Recursively calculates the total size of a folder in MB.
    """
    try:
        total_size = 0
        for dirpath, _, filenames in os.walk(folderpath):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return round(total_size / (1024 * 1024), 2)  # Convert to MB
    except Exception as e:
        log_error(f"Error getting folder size: {e}")
        return None

def get_current_time(format_str="%H:%M:%S"):
    """
    Returns current time formatted as desired.
    Default: "HH:MM:SS"
    """
    try:
        return datetime.now().strftime(format_str)
    except Exception as e:
        log_error(f"Error getting current time: {e}")
        return ""

def get_current_date(format_str="%Y-%m-%d"):
    """
    Returns current date formatted as desired.
    Default: "YYYY-MM-DD"
    """
    try:
        return datetime.now().strftime(format_str)
    except Exception as e:
        log_error(f"Error getting current date: {e}")
        return ""

def contains_keyword(text, keywords):
    """
    Checks if any of the given keywords are in the text.
    Useful for command matching.
    """
    try:
        if isinstance(keywords, str):
            return keywords.lower() in text.lower()
        elif isinstance(keywords, list):
            return any(kw.lower() in text.lower() for kw in keywords)
        return False
    except Exception as e:
        log_error(f"Error checking keyword match: {e}")
        return False