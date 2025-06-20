# skills/message_sender.py

import pywhatkit
import time

def send_whatsapp_message():
    Matrix().speech.speak("Who should I send the message to?")
    contact = Matrix().listener.wait_for_wake_word()
    Matrix().speech.speak("What's the message?")
    msg = Matrix().listener.wait_for_wake_word()
    Matrix().speech.speak("Sending message...")
    pywhatkit.sendwhatmsg_instantly(contact, msg)
    time.sleep(10)  # Wait for WhatsApp Web to load