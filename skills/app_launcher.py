# skills/app_launcher.py

import os
import json

# Lazy load Matrix speech engine to avoid circular import
def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

# Load app paths from config
try:
    with open("../../config/app_paths.json", "r") as f:
        APP_PATHS = json.load(f)
except Exception as e:
    print(f"[ERROR] Could not load app_paths.json: {e}")
    APP_PATHS = {}

def open_chrome():
    """Launch Google Chrome"""
    try:
        path = APP_PATHS.get("chrome")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Chrome")
        else:
            get_matrix_speech().speak("Chrome not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening Chrome")
        print(f"[ERROR] Failed to open Chrome: {e}")

def open_notepad():
    """Launch Notepad"""
    try:
        path = APP_PATHS.get("notepad")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Notepad")
        else:
            get_matrix_speech().speak("Notepad not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening Notepad")
        print(f"[ERROR] Failed to open Notepad: {e}")

def open_calculator():
    """Launch Calculator"""
    try:
        path = APP_PATHS.get("calculator")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Calculator")
        else:
            get_matrix_speech().speak("Calculator not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening Calculator")
        print(f"[ERROR] Failed to open Calculator: {e}")

def open_discord():
    try:
        path = APP_PATHS.get("discord")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Discord")
        else:
            get_matrix_speech().speak("Discord not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening Discord")
        print(f"[ERROR] Failed to open Discord: {e}")

def open_vscode():
    try:
        path = APP_PATHS.get("vscode")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Visual Studio Code")
        else:
            get_matrix_speech().speak("Visual Studio Code not found")
    except Exception as e:
        get_matrix_speech().speak("Error opening Visual Studio Code")
        print(f"[ERROR] Failed to open VS Code: {e}")

def open_whatsapp():
    try:
        path = APP_PATHS.get("whatsapp")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening WhatsApp")
        else:
            get_matrix_speech().speak("WhatsApp not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening WhatsApp")
        print(f"[ERROR] Failed to open WhatsApp: {e}")

def open_telegram():
    try:
        path = APP_PATHS.get("telegram")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Telegram")
        else:
            get_matrix_speech().speak("Telegram not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening Telegram")
        print(f"[ERROR] Failed to open Telegram: {e}")

def open_steam():
    try:
        path = APP_PATHS.get("steam")
        if path and os.path.exists(path):
            os.startfile(path)
            get_matrix_speech().speak("Opening Steam")
        else:
            get_matrix_speech().speak("Steam not found on your system")
    except Exception as e:
        get_matrix_speech().speak("Error opening Steam")
        print(f"[ERROR] Failed to open Steam: {e}")