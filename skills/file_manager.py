# skills/file_manager.py

import os
import logging
from core.logger import log_info, log_error

# Lazy import for Matrix to avoid circular dependencies
def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def create_folder(name):
    """
    Creates a folder with the given name if it doesn't exist.
    """
    try:
        if not os.path.exists(name):
            os.makedirs(name)
            message = f"Folder '{name}' created."
            log_info(message)
            get_matrix_speech().speak(message)
        else:
            message = f"Folder '{name}' already exists."
            log_info(message)
            get_matrix_speech().speak(message)
    except Exception as e:
        error_msg = f"Error creating folder '{name}': {e}"
        log_error(error_msg)
        get_matrix_speech().speak("I couldn't create that folder.")

def delete_file(name):
    """
    Deletes the specified file.
    """
    try:
        if os.path.isfile(name):
            os.remove(name)
            message = f"File '{name}' deleted."
            log_info(message)
            get_matrix_speech().speak(message)
        else:
            message = f"File '{name}' not found."
            log_info(message)
            get_matrix_speech().speak(message)
    except Exception as e:
        error_msg = f"Error deleting file '{name}': {e}"
        log_error(error_msg)
        get_matrix_speech().speak("I couldn't delete that file.")

def rename_file(old_name, new_name):
    """
    Renames a file from old_name to new_name.
    """
    try:
        if os.path.isfile(old_name):
            os.rename(old_name, new_name)
            message = f"File renamed to '{new_name}'."
            log_info(message)
            get_matrix_speech().speak(message)
        else:
            message = f"File '{old_name}' not found."
            log_info(message)
            get_matrix_speech().speak(message)
    except Exception as e:
        error_msg = f"Error renaming file '{old_name}': {e}"
        log_error(error_msg)
        get_matrix_speech().speak("I couldn't rename that file.")