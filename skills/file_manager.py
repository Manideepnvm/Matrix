# skills/file_manager.py

import os

def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def create_folder(name):
    try:
        if not os.path.exists(name):
            os.makedirs(name)
            get_matrix_speech().speak(f"Folder '{name}' created.")
        else:
            get_matrix_speech().speak(f"Folder '{name}' already exists.")
    except Exception as e:
        get_matrix_speech().speak("Error creating folder")

def delete_file(name):
    try:
        if os.path.isfile(name):
            os.remove(name)
            get_matrix_speech().speak(f"File '{name}' deleted.")
        else:
            get_matrix_speech().speak(f"File '{name}' not found.")
    except Exception as e:
        get_matrix_speech().speak("Error deleting file")