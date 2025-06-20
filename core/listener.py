# core/listener.py

from core.speech import SpeechEngine

class Listener:
    def __init__(self):
        self.speech = SpeechEngine()
        self.wake_word = "hey matrix"

    def wait_for_wake_word(self):
        while True:
            query = self.speech.listen()
            if self.wake_word in query:
                return query.replace(self.wake_word, "").strip()