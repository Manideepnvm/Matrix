# skills/app_launcher.py

import os
import json

def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

# Load app paths
try:
    with open("../../config/app_paths.json") as f:
        APP_PATHS = json.load(f)
except Exception as e:
    print(f"[ERROR] Could not load app_paths.json: {e}")
    APP_PATHS = {}

def open_chrome():
    try:
        path = APP_PATHS.get("chrome")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Chrome")
        else:
            get_matrix_speech().speak("Chrome not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening Chrome")

def open_notepad():
    try:
        path = APP_PATHS.get("notepad")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Notepad")
        else:
            get_matrix_speech().speak("Notepad not found")
    except Exception as e:
        get_matrix_speech().speak("Error opening Notepad")

def open_calculator():
    try:
        path = APP_PATHS.get("calculator")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Calculator")
        else:
            get_matrix_speech().speak("Calculator not found")
    except Exception as e:
        get_matrix_speech().speak("Error opening Calculator")