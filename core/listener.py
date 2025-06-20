# core/listener.py

import logging
from core.speech import SpeechEngine
from core.logger import log_info, log_error

class Listener:
    def __init__(self):
        self.speech = SpeechEngine()
        self.wake_word = "hey matrix"  # Make sure this matches settings.json

    def wait_for_wake_word(self):
        """
        Continuously listens until the wake word is detected.
        Returns any additional text after the wake word.
        """
        logging.info("Listening for wake word...")
        print("Listening for wake word...")

        while True:
            try:
                query = self.speech.listen()
                if not query:
                    continue

                logging.debug(f"Heard: {query}")
                print(f"Heard: {query}")

                if self.wake_word.lower() in query.lower():
                    logging.info("Wake word detected!")
                    # Remove wake word and return the rest of the command
                    clean_query = query.lower().replace(self.wake_word.lower(), "").strip()
                    return clean_query

            except Exception as e:
                log_error(f"Error in wake word detection: {e}")
                logging.warning("Microphone error or no audio input. Retrying...")