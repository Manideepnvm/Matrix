# skills/system_info.py

import psutil
import logging
from core.logger import log_info, log_error

# Lazy import to avoid circular dependency
def get_matrix_speech():
    from core.brain import Matrix
    return Matrix().speech

def get_battery_status():
    """
    Checks the battery percentage and speaks it aloud.
    Works on laptops and devices with a battery.
    """
    speech = get_matrix_speak()
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            message = "No battery found. This may be a desktop or device issue."
            log_info(message)
            speech.speak(message)
            return

        percent = battery.percent
        plugged = battery.power_plugged
        status = "plugged in" if plugged else "on battery power"

        message = f"Your battery is at {percent} percent and is {status}."
        log_info(f"Battery status: {percent}% - {status}")
        speech.speak(message)

    except Exception as e:
        error_msg = f"Error retrieving battery status: {e}"
        log_error(error_msg)
        speech.speak("I couldn't retrieve the battery status.")

def get_cpu_usage():
    """
    Gets current CPU usage and speaks it aloud.
    """
    speech = get_matrix_speak()
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        message = f"The CPU is currently at {cpu_percent} percent usage."
        log_info(f"CPU Usage: {cpu_percent}%")
        speech.speak(message)
    except Exception as e:
        error_msg = f"Error retrieving CPU usage: {e}"
        log_error(error_msg)
        speech.speak("I couldn't retrieve CPU usage.")

def get_memory_usage():
    """
    Gets current RAM usage and speaks it aloud.
    """
    speech = get_matrix_speak()
    try:
        memory = psutil.virtual_memory()
        total = round(memory.total / (1024 ** 3), 2)
        available = round(memory.available / (1024 ** 3), 2)
        percent_used = memory.percent
        used = round((memory.used / (1024 ** 3)), 2)

        message = f"You are using {used} gigabytes out of {total}, which is {percent_used} percent."
        log_info(f"Memory Usage: {used}/{total} GB ({percent_used}%)")
        speech.speak(message)
    except Exception as e:
        error_msg = f"Error retrieving memory usage: {e}"
        log_error(error_msg)
        speech.speak("I couldn't retrieve memory usage.")