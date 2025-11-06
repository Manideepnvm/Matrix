# core/brain.py

import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from core.speech import SpeechEngine
from core.listener import Listener
from core.logger import log_info, log_error, log_warning
from core.ui_manager import UIManager
from core.command_processor import CommandProcessor
from core.context_manager import ContextManager


# ---------------------------------------------
# ✅ Safe Import Handling for Skills
# ---------------------------------------------
def safe_import_skills():
    """Safely import all available skill modules."""
    imported_skills = {}
    skill_modules = [
        "app_launcher",
        "browser_control",
        "media_control",
        "system_info",
        "message_sender",
        "power_controls",
        "file_manager",
        "smart_home",
        "weather",
        "calendar_manager",
        "reminder_system",
        "music_player",
        "screen_capture"
    ]

    for module_name in skill_modules:
        try:
            imported_skills[module_name] = __import__(f"skills.{module_name}", fromlist=[module_name])
            log_info(f"Loaded skill: {module_name}")
        except ModuleNotFoundError:
            log_warning(f"Skill module '{module_name}' not found — skipping.")
        except ImportError as e:
            log_error(f"Failed to import skill '{module_name}': {e}")
        except Exception as e:
            log_error(f"Unexpected error importing skill '{module_name}': {e}")

    return imported_skills


# Load skills dynamically
skills = safe_import_skills()


# ---------------------------------------------
# ✅ Core Classes
# ---------------------------------------------
class AssistantState(Enum):
    """Enhanced state management for the assistant"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    WAKE_WORD_DETECTION = "wake_word_detection"
    ERROR = "error"


@dataclass
class MatrixConfig:
    """Configuration for Matrix assistant"""
    wake_word: str = "matrix"
    timeout: int = 15
    max_retry: int = 3
    confidence_threshold: float = 0.7
    enable_ui: bool = True
    enable_context: bool = True
    enable_learning: bool = True
    voice_feedback: bool = True


class Matrix:
    """Enhanced Matrix Voice Assistant with modern architecture"""

    def __init__(self, config: Optional[MatrixConfig] = None):
        self.config = config or MatrixConfig()

        # Core components
        self.speech = SpeechEngine()
        self.listener = Listener(wake_word=self.config.wake_word)
        self.command_processor = CommandProcessor(self)
        self.context = ContextManager() if self.config.enable_context else None
        self.ui = UIManager() if self.config.enable_ui else None

        # State & threading
        self.state = AssistantState.IDLE
        self.active = False
        self.running = True
        self.command_lock = threading.Lock()
        self.state_lock = threading.Lock()

        # Statistics
        self.stats = {
            'commands_processed': 0,
            'errors': 0,
            'uptime_start': time.time()
        }

        log_info("Matrix initialized successfully")

    # ---------------------------------------------
    # ✅ State Management
    # ---------------------------------------------
    def set_state(self, new_state: AssistantState):
        """Thread-safe state transition"""
        with self.state_lock:
            old_state = self.state
            self.state = new_state
            log_info(f"State transition: {old_state.value} -> {new_state.value}")
            if self.ui:
                self.ui.update_state(new_state.value)

    # ---------------------------------------------
    # ✅ Start Assistant
    # ---------------------------------------------
    def start(self):
        """Start the Matrix assistant"""
        try:
            log_info("Starting Matrix Voice Assistant...")

            # Launch UI in a separate thread
            if self.ui:
                ui_thread = threading.Thread(target=self.ui.run, daemon=True)
                ui_thread.start()
                time.sleep(1)  # Allow UI to initialize

            # Welcome Message
            self.speech.speak("Hello Sir, I am Matrix. All systems online and ready for your command.")
            self.set_state(AssistantState.WAKE_WORD_DETECTION)
            self._main_loop()

        except KeyboardInterrupt:
            log_info("Received shutdown signal.")
            self.shutdown()
        except Exception as e:
            log_error(f"Critical error in main loop: {e}")
            self.set_state(AssistantState.ERROR)
            self.shutdown()

    # ---------------------------------------------
    # ✅ Main Loop
    # ---------------------------------------------
    def _main_loop(self):
        """Main assistant processing loop"""
        while self.running:
            try:
                if not self.active:
                    self.wait_for_wake_word()
                else:
                    self.handle_commands()
            except Exception as e:
                log_error(f"Error in main loop: {e}")
                self.stats['errors'] += 1
                time.sleep(0.5)

    # ---------------------------------------------
    # ✅ Wake Word Detection
    # ---------------------------------------------
    def wait_for_wake_word(self):
        self.set_state(AssistantState.WAKE_WORD_DETECTION)
        command = self.speech.listen(timeout=5)

        if command and self.listener.detect_wake_word(command):
            self.active = True
            self.set_state(AssistantState.LISTENING)
            if self.ui:
                self.ui.trigger_activation()

            responses = [
                "Yes Sir?",
                "I'm listening.",
                "Ready for command.",
                "At your service."
            ]
            self.speech.speak(responses[self.stats['commands_processed'] % len(responses)])
            log_info("Wake word detected - Assistant activated")

    # ---------------------------------------------
    # ✅ Command Handling
    # ---------------------------------------------
    def handle_commands(self):
        start_time = time.time()
        last_command_time = time.time()

        while self.active and self.running:
            try:
                # Timeout handling
                if time.time() - last_command_time > self.config.timeout:
                    self.speech.speak("Timeout. Going to sleep mode.")
                    self.active = False
                    self.set_state(AssistantState.IDLE)
                    break

                # Listen for next command
                self.set_state(AssistantState.LISTENING)
                command = self.speech.listen(timeout=3)
                if not command:
                    continue

                log_info(f"User said: {command}")

                if self.ui:
                    self.ui.show_command(command)

                # Sleep or exit commands
                if self._check_exit_commands(command):
                    break

                # Process the command
                self.set_state(AssistantState.PROCESSING)
                with self.command_lock:
                    success = self.command_processor.process(command)

                if success:
                    self.stats['commands_processed'] += 1
                    last_command_time = time.time()
                    if self.context:
                        self.context.add_command(command)

                self.set_state(AssistantState.LISTENING)

            except Exception as e:
                log_error(f"Error handling command: {e}")
                self.speech.speak("Sorry, I encountered an error processing that command.")
                self.stats['errors'] += 1

    # ---------------------------------------------
    # ✅ Sleep & Exit Commands
    # ---------------------------------------------
    def _check_exit_commands(self, command: str) -> bool:
        exit_keywords = ["goodbye", "sleep", "standby", "deactivate", "stop listening"]
        for keyword in exit_keywords:
            if keyword in command.lower():
                responses = [
                    "Going to sleep mode. Say Matrix to wake me.",
                    "Entering standby. I'll be here when you need me.",
                    "Sleep mode activated."
                ]
                self.speech.speak(responses[0])
                self.active = False
                self.set_state(AssistantState.IDLE)
                if self.ui:
                    self.ui.trigger_deactivation()
                log_info("Sleep command detected")
                return True
        return False

    # ---------------------------------------------
    # ✅ Graceful Shutdown
    # ---------------------------------------------
    def shutdown(self):
        log_info("Shutting down Matrix...")
        self.running = False

        if self.config.voice_feedback:
            self.speech.speak("Shutting down. Goodbye Sir.")

        if self.ui:
            self.ui.close()

        uptime = time.time() - self.stats['uptime_start']
        log_info(f"Session stats - Commands: {self.stats['commands_processed']}, "
                 f"Errors: {self.stats['errors']}, Uptime: {uptime:.2f}s")
        log_info("Matrix shutdown complete")

    # ---------------------------------------------
    # ✅ Get Statistics
    # ---------------------------------------------
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            'uptime': time.time() - self.stats['uptime_start'],
            'state': self.state.value,
            'active': self.active
        }


# ---------------------------------------------
# ✅ Entry Point
# ---------------------------------------------
def main():
    config = MatrixConfig(
        wake_word="matrix",
        timeout=15,
        enable_ui=True,
        enable_context=True,
        voice_feedback=True
    )
    assistant = Matrix(config)
    assistant.start()


if __name__ == "__main__":
    main()
