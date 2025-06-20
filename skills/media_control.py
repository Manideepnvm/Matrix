# skills/media_control.py

import pyautogui
import logging
from core.logger import log_info, log_error

# Lazy import to avoid circular dependency
def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def play_music():
    """
    Simulates the Play/Pause media key.
    Works with most music players like Spotify, YouTube, VLC, etc.
    """
    try:
        pyautogui.press("playpause")
        message = "Playing or pausing music."
        log_info(message)
        get_matrix_speak().speak(message)
    except Exception as e:
        error_msg = f"Error playing/pausing music: {e}"
        log_error(error_msg)
        get_matrix_speak().speak("I couldn't control the music.")

def pause_music():
    """Simulates pressing the Pause key"""
    play_music()  # Most apps use the same key for play/pause

def next_track():
    """Skips to the next track"""
    try:
        pyautogui.press("nexttrack")
        message = "Skipping to next track."
        log_info(message)
        get_matrix_speak().speak(message)
    except Exception as e:
        error_msg = f"Error skipping track: {e}"
        log_error(error_msg)
        get_matrix_speak().speak("I couldn't skip to the next track.")

def prev_track():
    """Goes to the previous track"""
    try:
        pyautogui.press("prevtrack")
        message = "Going to previous track."
        log_info(message)
        get_matrix_speak().speak(message)
    except Exception as e:
        error_msg = f"Error going to previous track: {e}"
        log_error(error_msg)
        get_matrix_speak().speak("I couldn't go to the previous track.")

def volume_up():
    """Increases system volume"""
    try:
        pyautogui.press("volumeup")
        message = "Increasing volume."
        log_info(message)
        get_matrix_speak().speak(message)
    except Exception as e:
        error_msg = f"Error increasing volume: {e}"
        log_error(error_msg)
        get_matrix_speak().speak("I couldn't increase the volume.")

def volume_down():
    """Decreases system volume"""
    try:
        pyautogui.press("volumedown")
        message = "Decreasing volume."
        log_info(message)
        get_matrix_speak().speak(message)
    except Exception as e:
        error_msg = f"Error decreasing volume: {e}"
        log_error(error_msg)
        get_matrix_speak().speak("I couldn't decrease the volume.")

def mute_volume():
    """Mutes system volume"""
    try:
        pyautogui.press("volumemute")
        message = "Toggling mute."
        log_info(message)
        get_matrix_speak().speak(message)
    except Exception as e:
        error_msg = f"Error muting volume: {e}"
        log_error(error_msg)
        get_matrix_speak().speak("I couldn't mute the volume.")