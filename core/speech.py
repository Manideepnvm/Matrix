# core/speech.py

import pyttsx3
import speech_recognition as sr

class SpeechEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1)

    def speak(self, text):
        print(f"[MATRIX]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                return recognizer.recognize_google(audio).lower()
            except:
                return ""