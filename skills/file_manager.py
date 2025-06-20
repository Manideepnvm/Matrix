# skills/file_manager.py

import os

def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)
        Matrix().speech.speak(f"Folder '{name}' created.")
    else:
        Matrix().speech.speak(f"Folder '{name}' already exists.")

def delete_file(name):
    if os.path.isfile(name):
        os.remove(name)
        Matrix().speech.speak(f"File '{name}' deleted.")
    else:
        Matrix().speech.speak(f"File '{name}' not found.")

def rename_file(old_name, new_name):
    if os.path.isfile(old_name):
        os.rename(old_name, new_name)
        Matrix().speech.speak(f"File renamed to '{new_name}'.")
    else:
        Matrix().speech.speak(f"File '{old_name}' not found.")