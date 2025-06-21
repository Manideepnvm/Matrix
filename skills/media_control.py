# skills/media_control.py

import pyautogui

def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def play_music():
    try:
        pyautogui.press("playpause")
        get_matrix_speech().speak("Playing or pausing music")
    except Exception as e:
        get_matrix_speech().speak("Error controlling music")