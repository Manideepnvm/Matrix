# skills/power_controls.py

import os
import platform
import subprocess
import time
from typing import Optional
from enum import Enum

from core.logger import log_info, log_error, log_warning, log_critical


class PowerAction(Enum):
    """Available power actions"""
    SHUTDOWN = "shutdown"
    RESTART = "restart"
    SLEEP = "sleep"
    HIBERNATE = "hibernate"
    LOGOUT = "logout"
    LOCK = "lock"


class PowerController:
    """Enhanced power controller with safety features and multi-platform support"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.confirmation_required = True  # Safety feature
        self.countdown_seconds = 5  # Countdown before action
        
        # Statistics
        self.stats = {
            'shutdowns': 0,
            'restarts': 0,
            'sleeps': 0,
            'locks': 0,
            'cancelled': 0
        }
        
        log_info(f"Power Controller initialized on {self.platform}")
    
    def shutdown_pc(self, delay: int = 1, force: bool = False) -> bool:
        """
        Shutdown the system
        
        Args:
            delay: Delay in seconds before shutdown
            force: Force close all applications
            
        Returns:
            bool: True if command executed successfully
        """
        try:
            log_critical(f"SHUTDOWN requested with {delay}s delay")
            
            if self.platform == "windows":
                cmd = ["shutdown", "/s", "/t", str(delay)]
                if force:
                    cmd.append("/f")
                subprocess.Popen(cmd)
                
            elif self.platform == "darwin":  # macOS
                if delay > 0:
                    time.sleep(delay)
                subprocess.Popen([
                    "osascript", "-e",
                    'tell app "System Events" to shut down'
                ])
                
            else:  # Linux/Unix
                cmd = ["shutdown", "-h"]
                if delay > 0:
                    cmd.append(f"+{delay//60}")  # Convert to minutes
                else:
                    cmd.append("now")
                subprocess.Popen(cmd)
            
            self.stats['shutdowns'] += 1
            log_info("Shutdown command executed")
            return True
            
        except Exception as e:
            log_error(f"Error executing shutdown: {e}")
            # Fallback
            try:
                os.system("shutdown -h now")
                return True
            except:
                return False
    
    def restart_pc(self, delay: int = 1, force: bool = False) -> bool:
        """
        Restart the system
        
        Args:
            delay: Delay in seconds before restart
            force: Force close all applications
            
        Returns:
            bool: True if command executed successfully
        """
        try:
            log_critical(f"RESTART requested with {delay}s delay")
            
            if self.platform == "windows":
                cmd = ["shutdown", "/r", "/t", str(delay)]
                if force:
                    cmd.append("/f")
                subprocess.Popen(cmd)
                
            elif self.platform == "darwin":  # macOS
                if delay > 0:
                    time.sleep(delay)
                subprocess.Popen([
                    "osascript", "-e",
                    'tell app "System Events" to restart'
                ])
                
            else:  # Linux/Unix
                cmd = ["shutdown", "-r"]
                if delay > 0:
                    cmd.append(f"+{delay//60}")
                else:
                    cmd.append("now")
                subprocess.Popen(cmd)
            
            self.stats['restarts'] += 1
            log_info("Restart command executed")
            return True
            
        except Exception as e:
            log_error(f"Error executing restart: {e}")
            # Fallback
            try:
                os.system("shutdown -r now")
                return True
            except:
                return False
    
    def sleep_pc(self) -> bool:
        """
        Put system to sleep
        
        Returns:
            bool: True if command executed successfully
        """
        try:
            log_info("SLEEP requested")
            
            if self.platform == "windows":
                # Use rundll32 for sleep
                subprocess.Popen([
                    "rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"
                ])
                
            elif self.platform == "darwin":  # macOS
                subprocess.Popen([
                    "osascript", "-e",
                    'tell application "System Events" to sleep'
                ])
                
            else:  # Linux
                # Try systemctl first, then pm-suspend
                try:
                    subprocess.Popen(["systemctl", "suspend"])
                except:
                    subprocess.Popen(["pm-suspend"])
            
            self.stats['sleeps'] += 1
            log_info("Sleep command executed")
            return True
            
        except Exception as e:
            log_error(f"Error executing sleep: {e}")
            return False
    
    def hibernate_pc(self) -> bool:
        """
        Hibernate the system
        
        Returns:
            bool: True if command executed successfully
        """
        try:
            log_info("HIBERNATE requested")
            
            if self.platform == "windows":
                subprocess.Popen([
                    "rundll32.exe", "powrprof.dll,SetSuspendState", "Hibernate"
                ])
                
            elif self.platform == "darwin":  # macOS
                log_warning("Hibernate not directly supported on macOS")
                return False
                
            else:  # Linux
                try:
                    subprocess.Popen(["systemctl", "hibernate"])
                except:
                    subprocess.Popen(["pm-hibernate"])
            
            log_info("Hibernate command executed")
            return True
            
        except Exception as e:
            log_error(f"Error executing hibernate: {e}")
            return False
    
    def lock_screen(self) -> bool:
        """
        Lock the screen
        
        Returns:
            bool: True if command executed successfully
        """
        try:
            log_info("LOCK SCREEN requested")
            
            if self.platform == "windows":
                subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
                
            elif self.platform == "darwin":  # macOS
                subprocess.Popen([
                    "osascript", "-e",
                    'tell application "System Events" to keystroke "q" using {command down, control down}'
                ])
                
            else:  # Linux
                # Try multiple lock commands
                for cmd in [
                    ["gnome-screensaver-command", "--lock"],
                    ["xdg-screensaver", "lock"],
                    ["loginctl", "lock-session"]
                ]:
                    try:
                        subprocess.Popen(cmd)
                        break
                    except:
                        continue
            
            self.stats['locks'] += 1
            log_info("Lock screen command executed")
            return True
            
        except Exception as e:
            log_error(f"Error executing lock screen: {e}")
            return False
    
    def logout(self) -> bool:
        """
        Logout current user
        
        Returns:
            bool: True if command executed successfully
        """
        try:
            log_info("LOGOUT requested")
            
            if self.platform == "windows":
                subprocess.Popen(["shutdown", "/l"])
                
            elif self.platform == "darwin":  # macOS
                subprocess.Popen([
                    "osascript", "-e",
                    'tell application "System Events" to log out'
                ])
                
            else:  # Linux
                try:
                    subprocess.Popen(["gnome-session-quit", "--logout", "--no-prompt"])
                except:
                    subprocess.Popen(["loginctl", "terminate-user", os.getlogin()])
            
            log_info("Logout command executed")
            return True
            
        except Exception as e:
            log_error(f"Error executing logout: {e}")
            return False
    
    def cancel_shutdown(self) -> bool:
        """
        Cancel scheduled shutdown/restart
        
        Returns:
            bool: True if cancelled successfully
        """
        try:
            log_info("Cancelling shutdown/restart")
            
            if self.platform == "windows":
                subprocess.Popen(["shutdown", "/a"])
                
            elif self.platform == "darwin":  # macOS
                log_warning("Cannot cancel shutdown on macOS once initiated")
                return False
                
            else:  # Linux
                subprocess.Popen(["shutdown", "-c"])
            
            self.stats['cancelled'] += 1
            log_info("Shutdown cancelled")
            return True
            
        except Exception as e:
            log_error(f"Error cancelling shutdown: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get power controller statistics"""
        return {
            **self.stats,
            'platform': self.platform,
            'confirmation_required': self.confirmation_required
        }


# Global controller instance
_controller: Optional[PowerController] = None


def get_controller() -> PowerController:
    """Get or create global controller instance"""
    global _controller
    if _controller is None:
        _controller = PowerController()
    return _controller


def get_matrix_speech():
    """Get Matrix speech engine"""
    try:
        from core.speech import SpeechEngine
        return SpeechEngine()
    except:
        return None


# Convenience functions with voice feedback
def shutdown_pc(delay: int = 10, confirm: bool = True):
    """
    Shutdown the PC with voice feedback and optional confirmation
    
    Args:
        delay: Delay in seconds before shutdown
        confirm: Require voice confirmation
    """
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak(f"Shutting down the system in {delay} seconds.")
        
        log_warning(f"Shutdown initiated with {delay}s delay")
        
        # Confirmation check
        if confirm and speech:
            speech.speak("Say cancel to abort.")
            time.sleep(3)
            
            response = speech.listen(timeout=5)
            if response and "cancel" in response.lower():
                speech.speak("Shutdown cancelled")
                log_info("Shutdown cancelled by user")
                return
        
        # Execute shutdown
        success = controller.shutdown_pc(delay=delay)
        
        if not success:
            if speech:
                speech.speak("Failed to shutdown system")
            log_error("Shutdown command failed")
    
    except Exception as e:
        log_error(f"Error in shutdown_pc: {e}")
        if speech:
            speech.speak("Error shutting down system")


def restart_pc(delay: int = 10, confirm: bool = True):
    """
    Restart the PC with voice feedback and optional confirmation
    
    Args:
        delay: Delay in seconds before restart
        confirm: Require voice confirmation
    """
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak(f"Restarting the system in {delay} seconds.")
        
        log_warning(f"Restart initiated with {delay}s delay")
        
        # Confirmation check
        if confirm and speech:
            speech.speak("Say cancel to abort.")
            time.sleep(3)
            
            response = speech.listen(timeout=5)
            if response and "cancel" in response.lower():
                speech.speak("Restart cancelled")
                log_info("Restart cancelled by user")
                return
        
        # Execute restart
        success = controller.restart_pc(delay=delay)
        
        if not success:
            if speech:
                speech.speak("Failed to restart system")
            log_error("Restart command failed")
    
    except Exception as e:
        log_error(f"Error in restart_pc: {e}")
        if speech:
            speech.speak("Error restarting system")


def sleep_pc():
    """Put PC to sleep"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak("Putting system to sleep")
        
        success = controller.sleep_pc()
        
        if not success and speech:
            speech.speak("Failed to sleep system")
    
    except Exception as e:
        log_error(f"Error in sleep_pc: {e}")


def lock_screen():
    """Lock the screen"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak("Locking screen")
        
        success = controller.lock_screen()
        
        if not success and speech:
            speech.speak("Failed to lock screen")
    
    except Exception as e:
        log_error(f"Error in lock_screen: {e}")


def logout():
    """Logout current user"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak("Logging out")
        
        success = controller.logout()
        
        if not success and speech:
            speech.speak("Failed to logout")
    
    except Exception as e:
        log_error(f"Error in logout: {e}")


def cancel_shutdown():
    """Cancel scheduled shutdown or restart"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        success = controller.cancel_shutdown()
        
        if success:
            if speech:
                speech.speak("Shutdown cancelled successfully")
        else:
            if speech:
                speech.speak("Could not cancel shutdown")
    
    except Exception as e:
        log_error(f"Error in cancel_shutdown: {e}")