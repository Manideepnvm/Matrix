# skills/message_sender.py

import pywhatkit
import pyautogui
import time
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum

from core.logger import log_info, log_error, log_warning, log_debug


class MessagePlatform(Enum):
    """Available messaging platforms"""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"


class MessageSender:
    """Enhanced message sender with multiple platforms and contact management"""
    
    def __init__(self, contacts_file: str = "config/contacts.json"):
        self.contacts_file = Path(contacts_file)
        self.contacts = self._load_contacts()
        
        # Message history
        self.history = []
        self.max_history = 100
        
        # Statistics
        self.stats = {
            'total_sent': 0,
            'whatsapp_sent': 0,
            'failed': 0,
            'by_contact': {}
        }
        
        log_info("Message Sender initialized")
    
    def _load_contacts(self) -> Dict[str, Dict]:
        """Load contacts from file"""
        try:
            if self.contacts_file.exists():
                with open(self.contacts_file, 'r') as f:
                    contacts = json.load(f)
                log_info(f"Loaded {len(contacts)} contacts")
                return contacts
            else:
                log_warning("No contacts file found, starting with empty contacts")
                return {}
        except Exception as e:
            log_error(f"Error loading contacts: {e}")
            return {}
    
    def _save_contacts(self):
        """Save contacts to file"""
        try:
            self.contacts_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.contacts_file, 'w') as f:
                json.dump(self.contacts, f, indent=4)
            log_info("Contacts saved")
        except Exception as e:
            log_error(f"Error saving contacts: {e}")
    
    def add_contact(self, name: str, phone: str, email: Optional[str] = None) -> bool:
        """
        Add a new contact
        
        Args:
            name: Contact name
            phone: Phone number (with country code, e.g., +919876543210)
            email: Optional email address
            
        Returns:
            bool: True if added successfully
        """
        try:
            name_lower = name.lower()
            
            self.contacts[name_lower] = {
                'name': name,
                'phone': phone,
                'email': email,
                'added_date': datetime.now().isoformat()
            }
            
            self._save_contacts()
            log_info(f"Added contact: {name}")
            return True
            
        except Exception as e:
            log_error(f"Error adding contact: {e}")
            return False
    
    def get_contact(self, name: str) -> Optional[Dict]:
        """Get contact by name (fuzzy search)"""
        name_lower = name.lower()
        
        # Exact match
        if name_lower in self.contacts:
            return self.contacts[name_lower]
        
        # Fuzzy match
        for contact_name, contact_data in self.contacts.items():
            if name_lower in contact_name or contact_name in name_lower:
                log_debug(f"Fuzzy matched '{name}' to '{contact_name}'")
                return contact_data
        
        return None
    
    def send_whatsapp_instant(self, phone: str, message: str) -> bool:
        """
        Send WhatsApp message instantly
        
        Args:
            phone: Phone number with country code
            message: Message text
            
        Returns:
            bool: True if sent successfully
        """
        try:
            log_info(f"Sending WhatsApp message to {phone}")
            
            # Send message using pywhatkit
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone,
                message=message,
                wait_time=15,  # Wait for WhatsApp Web to load
                tab_close=False,
                close_time=3
            )
            
            # Wait and press enter to send
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Update statistics
            self.stats['total_sent'] += 1
            self.stats['whatsapp_sent'] += 1
            
            # Add to history
            self._add_to_history('whatsapp', phone, message)
            
            log_info("WhatsApp message sent successfully")
            return True
            
        except Exception as e:
            log_error(f"Error sending WhatsApp message: {e}")
            self.stats['failed'] += 1
            return False
    
    def send_whatsapp_scheduled(self, phone: str, message: str, 
                               hour: int, minute: int) -> bool:
        """
        Schedule WhatsApp message for later
        
        Args:
            phone: Phone number with country code
            message: Message text
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            bool: True if scheduled successfully
        """
        try:
            log_info(f"Scheduling WhatsApp message to {phone} at {hour}:{minute}")
            
            pywhatkit.sendwhatmsg(
                phone_no=phone,
                message=message,
                time_hour=hour,
                time_min=minute,
                wait_time=15,
                tab_close=True,
                close_time=3
            )
            
            log_info("WhatsApp message scheduled")
            return True
            
        except Exception as e:
            log_error(f"Error scheduling WhatsApp message: {e}")
            return False
    
    def send_to_contact(self, contact_name: str, message: str, 
                       platform: MessagePlatform = MessagePlatform.WHATSAPP) -> bool:
        """
        Send message to a saved contact
        
        Args:
            contact_name: Name of the contact
            message: Message text
            platform: Platform to use
            
        Returns:
            bool: True if sent successfully
        """
        contact = self.get_contact(contact_name)
        
        if not contact:
            log_warning(f"Contact not found: {contact_name}")
            return False
        
        if platform == MessagePlatform.WHATSAPP:
            phone = contact.get('phone')
            if not phone:
                log_warning(f"No phone number for contact: {contact_name}")
                return False
            
            success = self.send_whatsapp_instant(phone, message)
            
            if success:
                # Update contact stats
                name_lower = contact_name.lower()
                self.stats['by_contact'][name_lower] = \
                    self.stats['by_contact'].get(name_lower, 0) + 1
            
            return success
        
        # Add support for other platforms here
        log_warning(f"Platform not supported: {platform.value}")
        return False
    
    def send_group_message(self, group_id: str, message: str) -> bool:
        """
        Send message to WhatsApp group
        
        Args:
            group_id: WhatsApp group ID/link
            message: Message text
            
        Returns:
            bool: True if sent successfully
        """
        try:
            log_info(f"Sending message to group: {group_id}")
            
            pywhatkit.sendwhatmsg_to_group_instantly(
                group_id=group_id,
                message=message,
                wait_time=15,
                tab_close=False,
                close_time=3
            )
            
            time.sleep(2)
            pyautogui.press('enter')
            
            self.stats['total_sent'] += 1
            self.stats['whatsapp_sent'] += 1
            
            log_info("Group message sent")
            return True
            
        except Exception as e:
            log_error(f"Error sending group message: {e}")
            self.stats['failed'] += 1
            return False
    
    def _add_to_history(self, platform: str, recipient: str, message: str):
        """Add message to history"""
        entry = {
            'platform': platform,
            'recipient': recipient,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.history.append(entry)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_recent_messages(self, count: int = 10) -> List[Dict]:
        """Get recent message history"""
        return self.history[-count:]
    
    def list_contacts(self) -> List[str]:
        """Get list of all contact names"""
        return sorted([contact['name'] for contact in self.contacts.values()])
    
    def get_stats(self) -> Dict:
        """Get messaging statistics"""
        return {
            **self.stats,
            'total_contacts': len(self.contacts),
            'history_size': len(self.history)
        }


# Global sender instance
_sender: Optional[MessageSender] = None


def get_sender() -> MessageSender:
    """Get or create global sender instance"""
    global _sender
    if _sender is None:
        _sender = MessageSender()
    return _sender


def get_matrix():
    """Get Matrix instance (lazy import to avoid circular dependency)"""
    try:
        from core.brain import Matrix
        return Matrix()
    except:
        return None


def get_matrix_speech():
    """Get Matrix speech engine"""
    try:
        from core.speech import SpeechEngine
        return SpeechEngine()
    except:
        return None


# Main WhatsApp messaging function
def send_whatsapp_message():
    """
    Interactive function to send WhatsApp message
    Asks for contact and message via voice
    """
    sender = get_sender()
    matrix = get_matrix()
    
    if not matrix:
        log_error("Could not get Matrix instance")
        return
    
    speech = matrix.speech
    
    try:
        # Ask for contact
        speech.speak("Who should I send the message to?")
        time.sleep(1)
        
        contact_name = speech.listen(timeout=10)
        
        if not contact_name:
            speech.speak("No contact provided. Message cancelled.")
            log_info("WhatsApp message cancelled: No contact provided")
            return
        
        log_debug(f"Contact name heard: {contact_name}")
        
        # Get contact info
        contact = sender.get_contact(contact_name)
        
        if not contact:
            speech.speak(f"I don't have {contact_name} in contacts. Please provide phone number.")
            
            phone = speech.listen(timeout=10)
            
            if not phone:
                speech.speak("No phone number provided. Message cancelled.")
                return
            
            # Clean phone number (remove spaces, dashes)
            phone = phone.replace(" ", "").replace("-", "")
            
            # Ensure it starts with +
            if not phone.startswith("+"):
                speech.speak("Please include country code with plus sign")
                return
            
            contact = {'phone': phone, 'name': contact_name}
        
        # Ask for message
        speech.speak("What's the message?")
        time.sleep(1)
        
        message = speech.listen(timeout=15, phrase_time_limit=10)
        
        if not message:
            speech.speak("No message provided. Message cancelled.")
            log_info("WhatsApp message cancelled: No message provided")
            return
        
        log_debug(f"Message to send: {message}")
        
        # Confirm before sending
        speech.speak(f"Sending message to {contact['name']}: {message}. Confirm?")
        time.sleep(1)
        
        confirmation = speech.listen(timeout=5)
        
        if confirmation and any(word in confirmation.lower() for word in ['yes', 'confirm', 'send', 'ok']):
            speech.speak("Sending message. Please wait.")
            
            # Send message
            success = sender.send_whatsapp_instant(contact['phone'], message)
            
            if success:
                speech.speak(f"Message sent to {contact['name']}")
                log_info(f"WhatsApp message sent successfully to {contact['name']}")
            else:
                speech.speak("Sorry, I couldn't send the message.")
                log_error("Failed to send WhatsApp message")
        else:
            speech.speak("Message cancelled")
            log_info("User cancelled message sending")
    
    except Exception as e:
        log_error(f"Error in send_whatsapp_message: {e}", exc_info=True)
        speech = get_matrix_speech()
        if speech:
            speech.speak("I couldn't send that message. Please check logs for details.")


def send_quick_message(contact_name: str, message: str):
    """
    Send WhatsApp message directly without voice interaction
    
    Args:
        contact_name: Name of the contact
        message: Message to send
    """
    sender = get_sender()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak(f"Sending message to {contact_name}")
        
        success = sender.send_to_contact(contact_name, message)
        
        if success:
            if speech:
                speech.speak("Message sent successfully")
        else:
            if speech:
                speech.speak("Failed to send message")
    
    except Exception as e:
        log_error(f"Error in send_quick_message: {e}")
        if speech:
            speech.speak("Error sending message")


def add_contact(name: str, phone: str, email: Optional[str] = None):
    """Add a new contact"""
    sender = get_sender()
    speech = get_matrix_speech()
    
    try:
        if sender.add_contact(name, phone, email):
            if speech:
                speech.speak(f"Contact {name} added successfully")
            log_info(f"Contact added: {name}")
        else:
            if speech:
                speech.speak("Failed to add contact")
    except Exception as e:
        log_error(f"Error adding contact: {e}")


def list_contacts():
    """List all saved contacts"""
    sender = get_sender()
    speech = get_matrix_speech()
    
    try:
        contacts = sender.list_contacts()
        
        if speech:
            if contacts:
                speech.speak(f"You have {len(contacts)} contacts: {', '.join(contacts[:5])}")
            else:
                speech.speak("You have no saved contacts")
        
        return contacts
    except Exception as e:
        log_error(f"Error listing contacts: {e}")
        return []