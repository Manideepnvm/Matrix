# skills/system_info.py

import psutil

def get_battery_status():
    battery = psutil.sensors_battery()
    percent = battery.percent
    Matrix().speech.speak(f"Your battery is at {percent}%")