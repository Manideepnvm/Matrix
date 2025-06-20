# skills/app_launcher.py

import os
import json

with open("../../config/app_paths.json") as f:
    APP_PATHS = json.load(f)

def open_chrome():
    os.startfile(APP_PATHS["chrome"])
    Matrix().speech.speak("Opening Chrome")

def open_notepad():
    os.startfile(APP_PATHS["notepad"])
    Matrix().speech.speak("Opening Notepad")

def open_calculator():
    os.startfile(APP_PATHS["calculator"])
    Matrix().speech.speak("Opening Calculator")