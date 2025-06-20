# core/speech.py

import pyttsx3
import speech_recognition as sr
import logging
from core.logger import log_info, log_error

class SpeechEngine:
    def __init__(self):
        """Initialize the TTS engine and set default properties"""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)       # Speed of speech
        self.engine.setProperty('volume', 1.0)     # Volume level (0.0 to 1.0)
        self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)  # Use first voice (male/female can be changed)

    def speak(self, text):
        """Speak the given text out loud"""
        print(f"[MATRIX]: {text}")
        log_info(f"Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout=5, phrase_time_limit=5):
        """
        Listen for audio input from the user and convert it to text.
        
        Args:
            timeout (int): Max time to wait for speech
            phrase_time_limit (int): Max duration of speech to capture
        
        Returns:
            str: Recognized text or empty string if failed
        """
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            log_info("Listening for user input...")

            try:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Recognizing speech...")
                text = recognizer.recognize_google(audio).lower()
                log_info(f"Recognized: {text}")
                return text
            except sr.WaitTimeoutError:
                log_error("Listening timed out.")
                return ""
            except sr.UnknownValueError:
                log_error("Could not understand audio.")
                return ""
            except sr.RequestError as e:
                log_error(f"Speech recognition service error: {e}")
                return ""
            except Exception as e:
                log_error(f"Unexpected error during listening: {e}")
                return ""