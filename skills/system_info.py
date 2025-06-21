# skills/system_info.py

import psutil

def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def get_battery_status():
    try:
        battery = psutil.sensors_battery()
        percent = battery.percent
        plugged = battery.power_plugged
        status = "plugged in" if plugged else "on battery power"
        get_matrix_speech().speak(f"Your battery is at {percent} percent and is {status}.")
    except Exception as e:
        get_matrix_speech().speak("Error retrieving battery status")