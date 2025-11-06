# skills/media_control.py

import pyautogui
import time
from typing import Optional
from enum import Enum

from core.logger import log_info, log_error, log_warning, log_debug

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    log_warning("pycaw not available - volume control will be limited")


class MediaAction(Enum):
    """Media control actions"""
    PLAY_PAUSE = "playpause"
    PLAY = "play"
    PAUSE = "pause"
    NEXT = "nexttrack"
    PREVIOUS = "prevtrack"
    STOP = "stop"
    VOLUME_UP = "volumeup"
    VOLUME_DOWN = "volumedown"
    VOLUME_MUTE = "volumemute"


class MediaController:
    """Enhanced media controller with system-level controls"""
    
    def __init__(self):
        self.current_volume = 0.5  # Default volume level
        self.is_muted = False
        
        # Initialize volume control (Windows)
        self.volume_interface = None
        if PYCAW_AVAILABLE:
            try:
                self._init_volume_control()
            except Exception as e:
                log_warning(f"Could not initialize volume control: {e}")
        
        # Statistics
        self.stats = {
            'total_commands': 0,
            'play_pause_count': 0,
            'next_count': 0,
            'previous_count': 0,
            'volume_changes': 0
        }
        
        log_info("Media Controller initialized")
    
    def _init_volume_control(self):
        """Initialize Windows volume control interface"""
        if not PYCAW_AVAILABLE:
            return
        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            
            # Get current volume
            self.current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            self.is_muted = bool(self.volume_interface.GetMute())
            
            log_info("Volume control initialized")
        except Exception as e:
            log_error(f"Error initializing volume control: {e}")
    
    def play_pause(self) -> bool:
        """Toggle play/pause"""
        try:
            pyautogui.press(MediaAction.PLAY_PAUSE.value)
            self.stats['play_pause_count'] += 1
            self.stats['total_commands'] += 1
            log_info("Play/Pause toggled")
            return True
        except Exception as e:
            log_error(f"Error toggling play/pause: {e}")
            return False
    
    def play(self) -> bool:
        """Play media"""
        try:
            pyautogui.press(MediaAction.PLAY.value)
            self.stats['total_commands'] += 1
            log_info("Play command sent")
            return True
        except Exception as e:
            log_error(f"Error sending play command: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause media"""
        try:
            pyautogui.press(MediaAction.PAUSE.value)
            self.stats['total_commands'] += 1
            log_info("Pause command sent")
            return True
        except Exception as e:
            log_error(f"Error sending pause command: {e}")
            return False
    
    def next_track(self) -> bool:
        """Skip to next track"""
        try:
            pyautogui.press(MediaAction.NEXT.value)
            self.stats['next_count'] += 1
            self.stats['total_commands'] += 1
            log_info("Next track command sent")
            return True
        except Exception as e:
            log_error(f"Error skipping to next track: {e}")
            return False
    
    def previous_track(self) -> bool:
        """Go to previous track"""
        try:
            pyautogui.press(MediaAction.PREVIOUS.value)
            self.stats['previous_count'] += 1
            self.stats['total_commands'] += 1
            log_info("Previous track command sent")
            return True
        except Exception as e:
            log_error(f"Error going to previous track: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop media playback"""
        try:
            pyautogui.press(MediaAction.STOP.value)
            self.stats['total_commands'] += 1
            log_info("Stop command sent")
            return True
        except Exception as e:
            log_error(f"Error stopping playback: {e}")
            return False
    
    def volume_up(self, steps: int = 1) -> bool:
        """Increase volume"""
        try:
            for _ in range(steps):
                pyautogui.press(MediaAction.VOLUME_UP.value)
                time.sleep(0.1)
            
            self.stats['volume_changes'] += 1
            self.stats['total_commands'] += 1
            log_info(f"Volume increased by {steps} steps")
            return True
        except Exception as e:
            log_error(f"Error increasing volume: {e}")
            return False
    
    def volume_down(self, steps: int = 1) -> bool:
        """Decrease volume"""
        try:
            for _ in range(steps):
                pyautogui.press(MediaAction.VOLUME_DOWN.value)
                time.sleep(0.1)
            
            self.stats['volume_changes'] += 1
            self.stats['total_commands'] += 1
            log_info(f"Volume decreased by {steps} steps")
            return True
        except Exception as e:
            log_error(f"Error decreasing volume: {e}")
            return False
    
    def set_volume(self, level: float) -> bool:
        """
        Set volume to specific level (0.0 to 1.0)
        
        Args:
            level: Volume level (0.0 = mute, 1.0 = max)
            
        Returns:
            bool: True if successful
        """
        if not PYCAW_AVAILABLE or not self.volume_interface:
            log_warning("Volume control not available")
            return False
        
        try:
            level = max(0.0, min(1.0, level))  # Clamp to valid range
            self.volume_interface.SetMasterVolumeLevelScalar(level, None)
            self.current_volume = level
            
            self.stats['volume_changes'] += 1
            log_info(f"Volume set to {level:.0%}")
            return True
        except Exception as e:
            log_error(f"Error setting volume: {e}")
            return False
    
    def get_volume(self) -> Optional[float]:
        """Get current volume level (0.0 to 1.0)"""
        if not PYCAW_AVAILABLE or not self.volume_interface:
            return self.current_volume
        
        try:
            volume = self.volume_interface.GetMasterVolumeLevelScalar()
            self.current_volume = volume
            return volume
        except Exception as e:
            log_error(f"Error getting volume: {e}")
            return None
    
    def mute(self) -> bool:
        """Mute audio"""
        if PYCAW_AVAILABLE and self.volume_interface:
            try:
                self.volume_interface.SetMute(1, None)
                self.is_muted = True
                log_info("Audio muted")
                return True
            except Exception as e:
                log_error(f"Error muting audio: {e}")
        
        # Fallback to keyboard
        try:
            pyautogui.press(MediaAction.VOLUME_MUTE.value)
            self.is_muted = True
            return True
        except Exception as e:
            log_error(f"Error muting via keyboard: {e}")
            return False
    
    def unmute(self) -> bool:
        """Unmute audio"""
        if PYCAW_AVAILABLE and self.volume_interface:
            try:
                self.volume_interface.SetMute(0, None)
                self.is_muted = False
                log_info("Audio unmuted")
                return True
            except Exception as e:
                log_error(f"Error unmuting audio: {e}")
        
        # Fallback to keyboard
        try:
            pyautogui.press(MediaAction.VOLUME_MUTE.value)
            self.is_muted = False
            return True
        except Exception as e:
            log_error(f"Error unmuting via keyboard: {e}")
            return False
    
    def toggle_mute(self) -> bool:
        """Toggle mute state"""
        try:
            pyautogui.press(MediaAction.VOLUME_MUTE.value)
            self.is_muted = not self.is_muted
            self.stats['total_commands'] += 1
            log_info(f"Mute toggled to: {self.is_muted}")
            return True
        except Exception as e:
            log_error(f"Error toggling mute: {e}")
            return False
    
    def fast_forward(self, seconds: int = 10) -> bool:
        """Fast forward (simulated with right arrow)"""
        try:
            presses = seconds // 5  # Approximate 5 seconds per press
            for _ in range(presses):
                pyautogui.press("right")
                time.sleep(0.1)
            
            log_info(f"Fast forwarded ~{seconds} seconds")
            return True
        except Exception as e:
            log_error(f"Error fast forwarding: {e}")
            return False
    
    def rewind(self, seconds: int = 10) -> bool:
        """Rewind (simulated with left arrow)"""
        try:
            presses = seconds // 5  # Approximate 5 seconds per press
            for _ in range(presses):
                pyautogui.press("left")
                time.sleep(0.1)
            
            log_info(f"Rewound ~{seconds} seconds")
            return True
        except Exception as e:
            log_error(f"Error rewinding: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get media controller statistics"""
        return {
            **self.stats,
            'current_volume': self.current_volume,
            'is_muted': self.is_muted,
            'volume_control_available': PYCAW_AVAILABLE and self.volume_interface is not None
        }


# Global controller instance
_controller: Optional[MediaController] = None


def get_controller() -> MediaController:
    """Get or create global controller instance"""
    global _controller
    if _controller is None:
        _controller = MediaController()
    return _controller


def get_matrix_speech():
    """Get Matrix speech engine"""
    try:
        from core.speech import SpeechEngine
        return SpeechEngine()
    except:
        return None


# Convenience functions
def play_music():
    """Play or pause music"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.play_pause():
            if speech:
                speech.speak("Playing or pausing music")
        else:
            if speech:
                speech.speak("Error controlling music")
    except Exception as e:
        log_error(f"Error in play_music: {e}")
        if speech:
            speech.speak("Error controlling music")


def pause_music():
    """Pause music"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.pause():
            if speech:
                speech.speak("Music paused")
        else:
            if speech:
                speech.speak("Error pausing music")
    except Exception as e:
        log_error(f"Error in pause_music: {e}")


def next_track():
    """Skip to next track"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.next_track():
            if speech:
                speech.speak("Next track")
        else:
            if speech:
                speech.speak("Error skipping track")
    except Exception as e:
        log_error(f"Error in next_track: {e}")


def previous_track():
    """Go to previous track"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.previous_track():
            if speech:
                speech.speak("Previous track")
        else:
            if speech:
                speech.speak("Error going back")
    except Exception as e:
        log_error(f"Error in previous_track: {e}")


def stop_music():
    """Stop music playback"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.stop():
            if speech:
                speech.speak("Stopping playback")
        else:
            if speech:
                speech.speak("Error stopping music")
    except Exception as e:
        log_error(f"Error in stop_music: {e}")


def volume_up(steps: int = 2):
    """Increase volume"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.volume_up(steps):
            if speech:
                speech.speak("Volume increased")
        else:
            if speech:
                speech.speak("Error adjusting volume")
    except Exception as e:
        log_error(f"Error in volume_up: {e}")


def volume_down(steps: int = 2):
    """Decrease volume"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.volume_down(steps):
            if speech:
                speech.speak("Volume decreased")
        else:
            if speech:
                speech.speak("Error adjusting volume")
    except Exception as e:
        log_error(f"Error in volume_down: {e}")


def set_volume(level: int):
    """
    Set volume to specific percentage
    
    Args:
        level: Volume percentage (0-100)
    """
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        level_float = level / 100.0
        if controller.set_volume(level_float):
            if speech:
                speech.speak(f"Volume set to {level} percent")
        else:
            if speech:
                speech.speak("Error setting volume")
    except Exception as e:
        log_error(f"Error in set_volume: {e}")


def mute():
    """Mute audio"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.mute():
            if speech:
                speech.speak("Audio muted")
    except Exception as e:
        log_error(f"Error in mute: {e}")


def unmute():
    """Unmute audio"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.unmute():
            if speech:
                speech.speak("Audio unmuted")
    except Exception as e:
        log_error(f"Error in unmute: {e}")


def toggle_mute():
    """Toggle mute"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if controller.toggle_mute():
            if speech:
                if controller.is_muted:
                    speech.speak("Muted")
                else:
                    speech.speak("Unmuted")
    except Exception as e:
        log_error(f"Error in toggle_mute: {e}")