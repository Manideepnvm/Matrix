# skills/power_controls.py

import os

def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def shutdown_pc():
    get_matrix_speech().speak("Shutting down the system.")
    os.system("shutdown /s /t 1")

def restart_pc():
    get_matrix_speech().speak("Restarting the system.")
    os.system("shutdown /r /t 1")