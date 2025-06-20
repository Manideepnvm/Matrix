# skills/power_controls.py

import os

def shutdown_pc():
    Matrix().speech.speak("Shutting down the system.")
    os.system("shutdown /s /t 1")

def restart_pc():
    Matrix().speech.speak("Restarting the system.")
    os.system("shutdown /r /t 1")