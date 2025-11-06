# core/context_manager.py

from typing import List, Dict, Optional
from datetime import datetime
from collections import deque

from core.logger import log_info, log_debug


class ContextManager:
    """Manages conversation context and command history"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.command_history = deque(maxlen=max_history)
        self.session_start = datetime.now()
        
        # Context variables
        self.last_query = None
        self.last_response = None
        self.user_preferences = {}
        
        log_info("Context Manager initialized")
    
    def add_command(self, command: str, response: Optional[str] = None):
        """
        Add command to history
        
        Args:
            command: User command
            response: System response
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'response': response
        }
        
        self.command_history.append(entry)
        self.last_query = command
        self.last_response = response
        
        log_debug(f"Added to context: {command}")
    
    def get_recent_commands(self, count: int = 5) -> List[Dict]:
        """Get recent commands"""
        return list(self.command_history)[-count:]
    
    def get_last_command(self) -> Optional[Dict]:
        """Get last command"""
        if self.command_history:
            return self.command_history[-1]
        return None
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        log_info("Context history cleared")
    
    def set_preference(self, key: str, value):
        """Set user preference"""
        self.user_preferences[key] = value
        log_debug(f"Preference set: {key} = {value}")
    
    def get_preference(self, key: str, default=None):
        """Get user preference"""
        return self.user_preferences.get(key, default)
    
    def get_session_duration(self) -> float:
        """Get session duration in seconds"""
        return (datetime.now() - self.session_start).total_seconds()