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
        self.timeout = 10  # seconds before going idle

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
        if "hey matrix" in command:
            self.active = True
            self.speech.speak("Yes Sir?")
            log_info("Wake word detected. Assistant activated.")

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
                start_time = time.time()  # reset timer
            elif "goodbye" in command or "sleep" in command:
                self.speech.speak("Going to sleep mode.")
                log_info("Sleep command received. Assistant deactivating.")
                self.active = False
            else:
                self.speech.speak("Waiting for Matrix command...")

            # Timeout after N seconds of silence
            if time.time() - start_time > self.timeout:
                self.speech.speak("No activity detected. Going idle.")
                log_info("Timeout reached. Assistant going idle.")
                self.active = False

    def process_short_command(self, command):
        log_info(f"Processing command: Matrix {command}")

        # App Launching
        if "open chrome" in command:
            app_launcher.open_chrome()
        elif "open notepad" in command:
            app_launcher.open_notepad()
        elif "open calculator" in command:
            app_launcher.open_calculator()
        elif "open discord" in command:
            app_launcher.open_discord()
        elif "open code" in command or "open vs code" in command:
            app_launcher.open_vscode()
        elif "open word" in command:
            app_launcher.open_word()
        elif "open excel" in command:
            app_launcher.open_excel()
        elif "open powerpoint" in command:
            app_launcher.open_powerpoint()
        elif "open steam" in command:
            app_launcher.open_steam()
        elif "open whatsapp" in command:
            app_launcher.open_whatsapp()
        elif "open telegram" in command:
            app_launcher.open_telegram()

        # Browser & Search
        elif "search for" in command:
            browser_control.search_web(command)

        # Media Control
        elif "play music" in command or "pause music" in command:
            media_control.play_music()

        # System Info
        elif "battery status" in command:
            system_info.get_battery_status()

        # Messaging
        elif "send message" in command:
            message_sender.send_whatsapp_message()

        # Power Controls
        elif "shutdown" in command:
            power_controls.shutdown_pc()
        elif "restart" in command:
            power_controls.restart_pc()

        # File Management
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
        
        # Unknown Command
        else:
            self.speech.speak("I didn't understand that command.")
            log_info(f"Unrecognized command: {command}")