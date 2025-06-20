# skills/power_controls.py

import os
import logging
from core.logger import log_info, log_error

# Lazy import to avoid circular dependency
def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def shutdown_pc():
    """
    Shuts down the computer after confirmation.
    """
    speech = get_matrix_speech()
    try:
        speech.speak("Are you sure you want to shut down the system?")
        # Optional: Add a confirmation listener here
        speech.speak("Shutting down the system.")
        log_info("Initiating system shutdown...")
        os.system("shutdown /s /t 1")
    except Exception as e:
        error_msg = f"Error initiating shutdown: {e}"
        log_error(error_msg)
        speech.speak("I couldn't shut down the system.")

def restart_pc():
    """
    Restarts the computer after confirmation.
    """
    speech = get_matrix_speak()
    try:
        speech.speak("Are you sure you want to restart the system?")
        # Optional: Add a confirmation listener here
        speech.speak("Restarting the system.")
        log_info("Initiating system restart...")
        os.system("shutdown /r /t 1")
    except Exception as e:
        error_msg = f"Error initiating restart: {e}"
        log_error(error_msg)
        speech.speak("I couldn't restart the system.")

def sleep_pc():
    """
    Puts the computer into sleep mode.
    Works only if the system supports it.
    """
    speech = get_matrix_speak()
    try:
        speech.speak("Putting the system to sleep.")
        log_info("Putting system to sleep...")
        os.system("rundll32.exe powrprof.dll, SetSuspendState 0,1,0")
    except Exception as e:
        error_msg = f"Error putting system to sleep: {e}"
        log_error(error_msg)
        speech.speak("I couldn't put the system to sleep.")