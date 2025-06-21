# core/listener.py

from core.speech import SpeechEngine
from core.logger import log_info, log_error

class Listener:
    def __init__(self):
        self.speech = SpeechEngine()
        self.wake_word = "hey matrix"

    def wait_for_wake_word(self):
        while True:
            query = self.speech.listen()
            if self.wake_word.lower() in query.lower():
                return query.replace(self.wake_word.lower(), "").strip()