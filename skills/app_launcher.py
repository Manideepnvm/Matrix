# skills/app_launcher.py

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, List
import winreg  # For Windows registry access

from core.logger import log_info, log_error, log_warning, log_debug


class AppLauncher:
    """Enhanced application launcher with automatic path detection"""
    
    def __init__(self, config_path: str = "config/app_paths.json"):
        self.config_path = Path(config_path)
        self.platform = platform.system()
        self.app_paths = self._load_config()
        
        # Auto-detect apps if config is empty or missing
        if not self.app_paths or len(self.app_paths) < 5:
            self._auto_detect_apps()
        
        log_info(f"AppLauncher initialized with {len(self.app_paths)} apps")
    
    def _load_config(self) -> Dict[str, str]:
        """Load application paths from config"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    paths = json.load(f)
                    log_info(f"Loaded {len(paths)} app paths from config")
                    return paths
            else:
                log_warning(f"Config file not found: {self.config_path}")
                return {}
        except Exception as e:
            log_error(f"Error loading app config: {e}")
            return {}
    
    def _save_config(self):
        """Save application paths to config"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.app_paths, f, indent=4)
            log_info("App paths saved to config")
        except Exception as e:
            log_error(f"Error saving app config: {e}")
    
    def _auto_detect_apps(self):
        """Automatically detect common applications"""
        log_info("Auto-detecting installed applications...")
        
        if self.platform == "Windows":
            self._detect_windows_apps()
        elif self.platform == "Linux":
            self._detect_linux_apps()
        elif self.platform == "Darwin":  # macOS
            self._detect_macos_apps()
        
        self._save_config()
        log_info(f"Auto-detected {len(self.app_paths)} applications")
    
    def _detect_windows_apps(self):
        """Detect Windows applications"""
        # Common Windows apps
        common_apps = {
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ],
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ],
            "notepad": [
                r"C:\Windows\System32\notepad.exe",
                r"C:\Windows\notepad.exe"
            ],
            "notepad++": [
                r"C:\Program Files\Notepad++\notepad++.exe",
                r"C:\Program Files (x86)\Notepad++\notepad++.exe"
            ],
            "calculator": [
                r"C:\Windows\System32\calc.exe",
                "calculator:"  # Windows 10+ UWP app
            ],
            "vscode": [
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\Code.exe")
            ],
            "spotify": [
                os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe")
            ],
            "discord": [
                os.path.expanduser(r"~\AppData\Local\Discord\Update.exe")
            ],
            "telegram": [
                os.path.expanduser(r"~\AppData\Roaming\Telegram Desktop\Telegram.exe")
            ],
            "vlc": [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            ],
            "excel": [
                r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE"
            ],
            "word": [
                r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"
            ],
            "powerpoint": [
                r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE"
            ]
        }
        
        # Check each app
        for app_name, paths in common_apps.items():
            for path in paths:
                if path.endswith(':') or (os.path.exists(path) and os.path.isfile(path)):
                    self.app_paths[app_name] = path
                    log_debug(f"Found {app_name}: {path}")
                    break
    
    def _detect_linux_apps(self):
        """Detect Linux applications"""
        common_apps = {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "code": "code",
            "vscode": "code",
            "calculator": "gnome-calculator",
            "terminal": "gnome-terminal",
            "files": "nautilus",
            "spotify": "spotify",
            "vlc": "vlc"
        }
        
        for app_name, command in common_apps.items():
            if self._command_exists(command):
                self.app_paths[app_name] = command
                log_debug(f"Found {app_name}: {command}")
    
    def _detect_macos_apps(self):
        """Detect macOS applications"""
        common_apps = {
            "chrome": "/Applications/Google Chrome.app",
            "firefox": "/Applications/Firefox.app",
            "safari": "/Applications/Safari.app",
            "vscode": "/Applications/Visual Studio Code.app",
            "calculator": "/System/Applications/Calculator.app",
            "terminal": "/System/Applications/Utilities/Terminal.app",
            "spotify": "/Applications/Spotify.app",
            "vlc": "/Applications/VLC.app"
        }
        
        for app_name, path in common_apps.items():
            if os.path.exists(path):
                self.app_paths[app_name] = path
                log_debug(f"Found {app_name}: {path}")
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except:
            return False
    
    def launch_app(self, app_name: str, args: Optional[List[str]] = None) -> bool:
        """
        Launch an application
        
        Args:
            app_name: Name of the app to launch
            args: Additional arguments to pass to the app
            
        Returns:
            bool: True if launched successfully
        """
        app_name = app_name.lower()
        
        if app_name not in self.app_paths:
            log_warning(f"App not found: {app_name}")
            return False
        
        path = self.app_paths[app_name]
        
        try:
            log_info(f"Launching {app_name}: {path}")
            
            if self.platform == "Windows":
                return self._launch_windows(path, args)
            elif self.platform == "Linux":
                return self._launch_linux(path, args)
            elif self.platform == "Darwin":
                return self._launch_macos(path, args)
            
        except Exception as e:
            log_error(f"Error launching {app_name}: {e}")
            return False
    
    def _launch_windows(self, path: str, args: Optional[List[str]] = None) -> bool:
        """Launch app on Windows"""
        try:
            if path.endswith(':'):  # UWP app
                os.system(f'start {path}')
            else:
                if args:
                    subprocess.Popen([path] + args)
                else:
                    os.startfile(path)
            return True
        except Exception as e:
            log_error(f"Windows launch error: {e}")
            return False
    
    def _launch_linux(self, command: str, args: Optional[List[str]] = None) -> bool:
        """Launch app on Linux"""
        try:
            cmd = [command]
            if args:
                cmd.extend(args)
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            log_error(f"Linux launch error: {e}")
            return False
    
    def _launch_macos(self, path: str, args: Optional[List[str]] = None) -> bool:
        """Launch app on macOS"""
        try:
            cmd = ['open', path]
            if args:
                cmd.extend(['--args'] + args)
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            log_error(f"macOS launch error: {e}")
            return False
    
    def add_custom_app(self, name: str, path: str):
        """Add a custom application"""
        self.app_paths[name.lower()] = path
        self._save_config()
        log_info(f"Added custom app: {name} -> {path}")
    
    def get_installed_apps(self) -> List[str]:
        """Get list of detected applications"""
        return sorted(list(self.app_paths.keys()))


# Global launcher instance
_launcher: Optional[AppLauncher] = None


def get_launcher() -> AppLauncher:
    """Get or create global launcher instance"""
    global _launcher
    if _launcher is None:
        _launcher = AppLauncher()
    return _launcher


def get_matrix_speech():
    """Get Matrix speech engine"""
    try:
        from core.speech import SpeechEngine
        return SpeechEngine()
    except:
        return None


# Application launch functions
def open_chrome():
    """Open Google Chrome browser"""
    launcher = get_launcher()
    speech = get_matrix_speech()
    
    try:
        if launcher.launch_app("chrome"):
            if speech:
                speech.speak("Opening Google Chrome")
            log_info("Chrome opened successfully")
        else:
            if speech:
                speech.speak("Chrome not found on your system")
            log_warning("Chrome not available")
    except Exception as e:
        if speech:
            speech.speak("Error opening Chrome")
        log_error(f"Error opening Chrome: {e}")


def open_firefox():
    """Open Firefox browser"""
    launcher = get_launcher()
    speech = get_matrix_speech()
    
    try:
        if launcher.launch_app("firefox"):
            if speech:
                speech.speak("Opening Firefox")
        else:
            if speech:
                speech.speak("Firefox not found")
    except Exception as e:
        if speech:
            speech.speak("Error opening Firefox")
        log_error(f"Error opening Firefox: {e}")


def open_notepad():
    """Open Notepad"""
    launcher = get_launcher()
    speech = get_matrix_speech()
    
    try:
        if launcher.launch_app("notepad"):
            if speech:
                speech.speak("Opening Notepad")
        else:
            if speech:
                speech.speak("Notepad not found")
    except Exception as e:
        if speech:
            speech.speak("Error opening Notepad")
        log_error(f"Error opening Notepad: {e}")


def open_calculator():
    """Open Calculator"""
    launcher = get_launcher()
    speech = get_matrix_speech()
    
    try:
        if launcher.launch_app("calculator"):
            if speech:
                speech.speak("Opening Calculator")
        else:
            if speech:
                speech.speak("Calculator not found")
    except Exception as e:
        if speech:
            speech.speak("Error opening Calculator")
        log_error(f"Error opening Calculator: {e}")


def open_vscode():
    """Open Visual Studio Code"""
    launcher = get_launcher()
    speech = get_matrix_speech()
    
    try:
        if launcher.launch_app("vscode"):
            if speech:
                speech.speak("Opening Visual Studio Code")
        else:
            if speech:
                speech.speak("VS Code not found")
    except Exception as e:
        if speech:
            speech.speak("Error opening VS Code")
        log_error(f"Error opening VS Code: {e}")


def open_spotify():
    """Open Spotify"""
    launcher = get_launcher()
    speech = get_matrix_speech()
    
    try:
        if launcher.launch_app("spotify"):
            if speech:
                speech.speak("Opening Spotify")
        else:
            if speech:
                speech.speak("Spotify not found")
    except Exception as e:
        if speech:
            speech.speak("Error opening Spotify")
        log_error(f"Error opening Spotify: {e}")


def open_app(app_name: str):
    """
    Open any registered application by name
    
    Args:
        app_name: Name of the app to open
    """
    launcher = get_launcher()
    speech = get_matrix_speech()
    
    try:
        if launcher.launch_app(app_name):
            if speech:
                speech.speak(f"Opening {app_name}")
        else:
            if speech:
                speech.speak(f"{app_name} not found")
    except Exception as e:
        if speech:
            speech.speak(f"Error opening {app_name}")
        log_error(f"Error opening {app_name}: {e}")


def list_available_apps():
    """List all available applications"""
    launcher = get_launcher()
    apps = launcher.get_installed_apps()
    
    speech = get_matrix_speech()
    if speech:
        if apps:
            speech.speak(f"I found {len(apps)} applications: {', '.join(apps[:5])}")
        else:
            speech.speak("No applications detected")
    
    return apps