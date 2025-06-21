# core/brain.py

import time

from core.speech import SpeechEngine
from core.listener import Listener
from core.logger import log_info, log_error

try:
    from skills import app_launcher, browser_control, media_control, \
        system_info, message_sender, power_controls, file_manager
except ImportError as e:
    log_error(f"Error importing skills: {e}")
    raise


class Matrix:
    def __init__(self):
        self.speech = SpeechEngine()
        self.listener = Listener()
        self.active = False
        self.timeout = 10

    def start(self):
        self.speech.speak("Hello Sir, I am Matrix. Ready for command.")
        while True:
            if not self.active:
                self.wait_for_wake_word()
            else:
                self.handle_commands()

    def wait_for_wake_word(self):
        command = self.speech.listen()
        if command == "":
            return
        if self.listener.wake_word in command:
            self.active = True
            self.speech.speak("Yes Sir?")

    def handle_commands(self):
        start_time = time.time()
        while self.active:
            command = self.speech.listen()
            if command == "":
                continue

            print(f"You said: {command}")
            log_info(f"User said: {command}")

            if "matrix" in command:
                clean_cmd = command.replace("matrix", "").strip()
                self.process_short_command(clean_cmd)
                start_time = time.time()
            elif "goodbye" in command or "sleep" in command:
                self.speech.speak("Going to sleep mode.")
                self.active = False
            else:
                self.speech.speak("Waiting for Matrix command...")

            if time.time() - start_time > self.timeout:
                self.speech.speak("No activity detected. Going idle.")
                self.active = False

    def process_short_command(self, command):
        log_info(f"Processing command: Matrix {command}")

        if "open chrome" in command:
            app_launcher.open_chrome()
        elif "open notepad" in command:
            app_launcher.open_notepad()
        elif "search for" in command:
            browser_control.search_web(command)
        elif "play music" in command:
            media_control.play_music()
        elif "battery status" in command:
            system_info.get_battery_status()
        elif "send message" in command:
            message_sender.send_whatsapp_message()
        elif "shutdown" in command:
            power_controls.shutdown_pc()
        elif "restart" in command:
            power_controls.restart_pc()
        elif "create folder" in command:
            folder_name = command.replace("create folder", "").strip()
            file_manager.create_folder(folder_name)
        elif "delete file" in command:
            file_name = command.replace("delete file", "").strip()
            file_manager.delete_file(file_name)
        elif "rename file" in command:
            parts = command.replace("rename file", "").strip().split("to")
            if len(parts) == 2:
                old_name, new_name = parts[0].strip(), parts[1].strip()
                file_manager.rename_file(old_name, new_name)
            else:
                self.speech.speak("Please specify the old and new name.")
        else:
            self.speech.speak("I didn't understand that command.")