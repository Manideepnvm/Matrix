# skills/media_control.py

import pyautogui

def play_music():
    pyautogui.press("playpause")
    Matrix().speech.speak("Playing or pausing music")