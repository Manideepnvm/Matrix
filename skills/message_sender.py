# skills/message_sender.py

import pywhatkit
import time
import logging
from core.logger import log_info, log_error

# Lazy import to avoid circular dependency
def get_matrix():
    from core.brain import Matrix
    return Matrix()

def send_whatsapp_message():
    """
    Sends a WhatsApp message to the specified contact.
    Asks:
        1. Who to send the message to
        2. What the message is
    """
    matrix = get_matrix()
    speech = matrix.speech
    listener = matrix.listener

    try:
        speech.speak("Who should I send the message to?")
        contact = listener.wait_for_wake_word()
        if not contact:
            speech.speak("No contact provided. Message cancelled.")
            log_info("WhatsApp message cancelled: No contact provided")
            return

        speech.speak("What's the message?")
        msg = listener.wait_for_wake_word()
        if not msg:
            speech.speak("No message provided. Message cancelled.")
            log_info("WhatsApp message cancelled: No message provided")
            return

        speech.speak(f"Sending message to {contact}...")
        log_info(f"Sending WhatsApp message to: {contact}, Message: {msg}")

        # Send WhatsApp message
        pywhatkit.sendwhatmsg_instantly(contact, msg)
        time.sleep(5)  # Wait for WhatsApp Web to load
        pyautogui.press('enter')  # Hit Enter to send (sometimes needed)

        speech.speak(f"Message sent to {contact}.")
        log_info("WhatsApp message sent successfully.")

    except Exception as e:
        error_msg = f"Error sending WhatsApp message: {e}"
        log_error(error_msg)
        speech.speak("I couldn't send that message.")