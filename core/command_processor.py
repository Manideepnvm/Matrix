# core/command_processor.py

import re
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from difflib import SequenceMatcher

from core.logger import log_info, log_error, log_warning, log_debug

# Import skills
from skills import (
    app_launcher, browser_control, media_control,
    system_info, message_sender, power_controls, file_manager
)


@dataclass
class Command:
    """Command definition"""
    patterns: List[str]
    handler: Callable
    description: str
    category: str
    requires_params: bool = False


class CommandProcessor:
    """Advanced command processor with fuzzy matching and context awareness"""
    
    def __init__(self, matrix_instance):
        self.matrix = matrix_instance
        self.commands = self._register_commands()
        self.command_history = []
        self.last_command = None
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'by_category': {}
        }
        
        log_info(f"Command Processor initialized with {len(self.commands)} commands")
    
    def _register_commands(self) -> List[Command]:
        """Register all available commands"""
        commands = [
            # Application Control
            Command(
                patterns=["open chrome", "launch chrome", "start chrome"],
                handler=app_launcher.open_chrome,
                description="Open Google Chrome",
                category="apps"
            ),
            Command(
                patterns=["open firefox", "launch firefox"],
                handler=app_launcher.open_firefox,
                description="Open Firefox",
                category="apps"
            ),
            Command(
                patterns=["open notepad", "launch notepad"],
                handler=app_launcher.open_notepad,
                description="Open Notepad",
                category="apps"
            ),
            Command(
                patterns=["open calculator", "launch calculator", "calculator"],
                handler=app_launcher.open_calculator,
                description="Open Calculator",
                category="apps"
            ),
            Command(
                patterns=["open vscode", "open code", "launch vscode"],
                handler=app_launcher.open_vscode,
                description="Open VS Code",
                category="apps"
            ),
            Command(
                patterns=["open spotify", "launch spotify", "start spotify"],
                handler=app_launcher.open_spotify,
                description="Open Spotify",
                category="apps"
            ),
            
            # Browser Control
            Command(
                patterns=["search for", "search", "google", "look up", "find"],
                handler=lambda cmd: browser_control.search_web(cmd),
                description="Search the web",
                category="browser",
                requires_params=True
            ),
            Command(
                patterns=["open youtube", "go to youtube"],
                handler=lambda: browser_control.open_website("youtube"),
                description="Open YouTube",
                category="browser"
            ),
            Command(
                patterns=["open gmail", "check email"],
                handler=browser_control.open_gmail,
                description="Open Gmail",
                category="browser"
            ),
            Command(
                patterns=["search youtube", "youtube search"],
                handler=lambda cmd: browser_control.search_youtube(cmd),
                description="Search YouTube",
                category="browser",
                requires_params=True
            ),
            Command(
                patterns=["open maps", "show maps", "google maps"],
                handler=lambda cmd: browser_control.open_maps(cmd),
                description="Open Google Maps",
                category="browser",
                requires_params=True
            ),
            
            # Media Control
            Command(
                patterns=["play music", "pause music", "play pause", "toggle music"],
                handler=media_control.play_music,
                description="Play/Pause music",
                category="media"
            ),
            Command(
                patterns=["next track", "next song", "skip"],
                handler=media_control.next_track,
                description="Next track",
                category="media"
            ),
            Command(
                patterns=["previous track", "previous song", "back"],
                handler=media_control.previous_track,
                description="Previous track",
                category="media"
            ),
            Command(
                patterns=["volume up", "increase volume", "louder"],
                handler=media_control.volume_up,
                description="Increase volume",
                category="media"
            ),
            Command(
                patterns=["volume down", "decrease volume", "quieter"],
                handler=media_control.volume_down,
                description="Decrease volume",
                category="media"
            ),
            Command(
                patterns=["mute", "unmute", "toggle mute"],
                handler=media_control.toggle_mute,
                description="Toggle mute",
                category="media"
            ),
            
            # System Info
            Command(
                patterns=["battery status", "battery level", "how much battery"],
                handler=system_info.get_battery_status,
                description="Get battery status",
                category="system"
            ),
            Command(
                patterns=["cpu usage", "processor usage", "cpu status"],
                handler=system_info.get_cpu_usage,
                description="Get CPU usage",
                category="system"
            ),
            Command(
                patterns=["memory usage", "ram usage", "memory status"],
                handler=system_info.get_memory_usage,
                description="Get memory usage",
                category="system"
            ),
            Command(
                patterns=["disk space", "storage space", "disk usage"],
                handler=system_info.get_disk_usage,
                description="Get disk usage",
                category="system"
            ),
            Command(
                patterns=["system status", "full status", "system info"],
                handler=system_info.get_full_status,
                description="Get full system status",
                category="system"
            ),
            
            # Power Controls
            Command(
                patterns=["shutdown", "shut down", "power off"],
                handler=power_controls.shutdown_pc,
                description="Shutdown PC",
                category="power"
            ),
            Command(
                patterns=["restart", "reboot"],
                handler=power_controls.restart_pc,
                description="Restart PC",
                category="power"
            ),
            Command(
                patterns=["sleep", "go to sleep"],
                handler=power_controls.sleep_pc,
                description="Put PC to sleep",
                category="power"
            ),
            Command(
                patterns=["lock screen", "lock"],
                handler=power_controls.lock_screen,
                description="Lock screen",
                category="power"
            ),
            
            # File Management
            Command(
                patterns=["create folder", "make folder", "new folder"],
                handler=lambda cmd: file_manager.create_folder(self._extract_param(cmd, "folder")),
                description="Create a folder",
                category="files",
                requires_params=True
            ),
            Command(
                patterns=["delete file", "remove file"],
                handler=lambda cmd: file_manager.delete_file(self._extract_param(cmd, "file")),
                description="Delete a file",
                category="files",
                requires_params=True
            ),
            Command(
                patterns=["search files", "find files"],
                handler=lambda cmd: file_manager.search_files(self._extract_param(cmd, "search")),
                description="Search for files",
                category="files",
                requires_params=True
            ),
            
            # Messaging
            Command(
                patterns=["send message", "send whatsapp", "whatsapp message"],
                handler=message_sender.send_whatsapp_message,
                description="Send WhatsApp message",
                category="communication"
            ),
        ]
        
        return commands
    
    def process(self, command_text: str) -> bool:
        """
        Process a command
        
        Args:
            command_text: Command text to process
            
        Returns:
            bool: True if command was handled successfully
        """
        if not command_text:
            return False
        
        self.stats['total_processed'] += 1
        command_lower = command_text.lower().strip()
        
        # Try to match command
        matched_command = self._match_command(command_lower)
        
        if matched_command:
            try:
                log_info(f"Executing command: {matched_command.description}")
                
                # Execute command
                if matched_command.requires_params:
                    matched_command.handler(command_lower)
                else:
                    matched_command.handler()
                
                # Update statistics
                self.stats['successful'] += 1
                category = matched_command.category
                self.stats['by_category'][category] = \
                    self.stats['by_category'].get(category, 0) + 1
                
                # Update history
                self.command_history.append({
                    'command': command_text,
                    'category': category,
                    'success': True
                })
                self.last_command = matched_command
                
                return True
                
            except Exception as e:
                log_error(f"Error executing command: {e}")
                self.stats['failed'] += 1
                self.matrix.speech.speak("Sorry, there was an error executing that command.")
                return False
        else:
            log_warning(f"Unknown command: {command_text}")
            self.stats['failed'] += 1
            self.matrix.speech.speak("I didn't understand that command. Please try again.")
            return False
    
    def _match_command(self, command_text: str) -> Optional[Command]:
        """
        Match command text to a registered command using fuzzy matching
        
        Args:
            command_text: Command text to match
            
        Returns:
            Matched Command or None
        """
        best_match = None
        best_score = 0.0
        threshold = 0.6  # Minimum similarity threshold
        
        for command in self.commands:
            for pattern in command.patterns:
                # Check for exact match
                if pattern in command_text:
                    return command
                
                # Fuzzy matching
                score = SequenceMatcher(None, command_text, pattern).ratio()
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = command
        
        if best_match:
            log_debug(f"Fuzzy matched with score {best_score:.2f}: {best_match.description}")
        
        return best_match
    
    def _extract_param(self, command_text: str, param_type: str) -> str:
        """
        Extract parameter from command text
        
        Args:
            command_text: Full command text
            param_type: Type of parameter to extract
            
        Returns:
            Extracted parameter
        """
        # Remove common command words
        keywords_to_remove = [
            "matrix", "create", "make", "new", "delete", "remove",
            "search", "find", "folder", "file", "for", "the", "a"
        ]
        
        words = command_text.split()
        filtered_words = [w for w in words if w.lower() not in keywords_to_remove]
        
        return " ".join(filtered_words).strip()
    
    def list_commands(self, category: Optional[str] = None) -> List[Command]:
        """
        List available commands
        
        Args:
            category: Optional category filter
            
        Returns:
            List of commands
        """
        if category:
            return [cmd for cmd in self.commands if cmd.category == category]
        return self.commands
    
    def get_categories(self) -> List[str]:
        """Get list of command categories"""
        return list(set(cmd.category for cmd in self.commands))
    
    def get_stats(self) -> Dict:
        """Get command processor statistics"""
        success_rate = 0.0
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total_processed']) * 100
        
        return {
            **self.stats,
            'success_rate': f"{success_rate:.1f}%",
            'total_commands_registered': len(self.commands),
            'categories': len(self.get_categories())
        }