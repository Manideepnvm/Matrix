# core/speech.py

import pyttsx3
import speech_recognition as sr
from typing import Optional, List, Callable
from dataclasses import dataclass
import threading
import queue
import time
from enum import Enum

from core.logger import log_info, log_error, log_warning, log_debug


class VoiceType(Enum):
    """Available voice types"""
    MALE = 0
    FEMALE = 1


class SpeechEngineMode(Enum):
    """Speech engine modes"""
    BLOCKING = "blocking"      # Wait for speech to complete
    NON_BLOCKING = "non_blocking"  # Queue speech and return immediately
    INTERRUPT = "interrupt"    # Interrupt current speech


@dataclass
class SpeechConfig:
    """Configuration for speech engine"""
    rate: int = 150              # Words per minute (50-300)
    volume: float = 1.0          # Volume level (0.0-1.0)
    voice_type: VoiceType = VoiceType.MALE
    pitch: int = 100             # Pitch (50-200)
    mode: SpeechEngineMode = SpeechEngineMode.NON_BLOCKING
    enable_effects: bool = True  # Enable special voice effects


@dataclass
class ListenerConfig:
    """Configuration for speech recognition"""
    timeout: int = 5             # Seconds to wait for phrase start
    phrase_time_limit: int = 5   # Max seconds for phrase
    energy_threshold: int = 4000 # Minimum audio energy to consider speech
    dynamic_energy: bool = True  # Adjust energy threshold dynamically
    pause_threshold: float = 0.8 # Seconds of silence to consider phrase complete
    language: str = "en-US"      # Recognition language
    prefer_offline: bool = False # Use offline recognition if available


class SpeechEngine:
    """Enhanced speech engine with advanced TTS and STT capabilities"""
    
    def __init__(self, config: Optional[SpeechConfig] = None):
        self.config = config or SpeechConfig()
        
        # Initialize TTS engine
        try:
            self.engine = pyttsx3.init()
            self._configure_tts()
            log_info("TTS engine initialized successfully")
        except Exception as e:
            log_error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
        
        # Speech queue for non-blocking mode
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread: Optional[threading.Thread] = None
        
        # Start speech worker thread
        if self.config.mode == SpeechEngineMode.NON_BLOCKING:
            self._start_speech_worker()
        
        # Statistics
        self.stats = {
            'total_speeches': 0,
            'total_listens': 0,
            'recognition_failures': 0,
            'recognition_successes': 0,
            'average_confidence': 0.0
        }
        
        log_info("Speech Engine initialized")

    def _configure_tts(self):
        """Configure TTS engine with settings"""
        if not self.engine:
            return
        
        try:
            # Set rate
            self.engine.setProperty('rate', self.config.rate)
            
            # Set volume
            self.engine.setProperty('volume', self.config.volume)
            
            # Set voice
            voices = self.engine.getProperty('voices')
            if voices:
                voice_index = self.config.voice_type.value
                if voice_index < len(voices):
                    self.engine.setProperty('voice', voices[voice_index].id)
                    log_debug(f"Voice set to: {voices[voice_index].name}")
            
            log_debug(f"TTS configured - Rate: {self.config.rate}, Volume: {self.config.volume}")
            
        except Exception as e:
            log_error(f"Error configuring TTS: {e}")

    def speak(self, text: str, mode: Optional[SpeechEngineMode] = None, 
              callback: Optional[Callable] = None) -> bool:
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
            mode: Override default speech mode
            callback: Function to call when speech completes
            
        Returns:
            bool: True if speech started successfully
        """
        if not text or not self.engine:
            return False
        
        mode = mode or self.config.mode
        self.stats['total_speeches'] += 1
        
        # Log and print
        print(f"[MATRIX]: {text}")
        log_info(f"Speaking: {text}")
        
        try:
            if mode == SpeechEngineMode.BLOCKING:
                return self._speak_blocking(text, callback)
            elif mode == SpeechEngineMode.NON_BLOCKING:
                return self._speak_non_blocking(text, callback)
            elif mode == SpeechEngineMode.INTERRUPT:
                return self._speak_interrupt(text, callback)
            
        except Exception as e:
            log_error(f"Error in speak: {e}")
            return False

    def _speak_blocking(self, text: str, callback: Optional[Callable] = None) -> bool:
        """Speak in blocking mode (wait for completion)"""
        try:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
            
            if callback:
                callback()
            
            return True
            
        except Exception as e:
            log_error(f"Error in blocking speech: {e}")
            self.is_speaking = False
            return False

    def _speak_non_blocking(self, text: str, callback: Optional[Callable] = None) -> bool:
        """Queue speech for non-blocking mode"""
        try:
            self.speech_queue.put((text, callback))
            return True
        except Exception as e:
            log_error(f"Error queuing speech: {e}")
            return False

    def _speak_interrupt(self, text: str, callback: Optional[Callable] = None) -> bool:
        """Interrupt current speech and speak immediately"""
        try:
            # Clear queue and stop current speech
            self.stop_speaking()
            
            # Speak immediately
            return self._speak_blocking(text, callback)
            
        except Exception as e:
            log_error(f"Error in interrupt speech: {e}")
            return False

    def _start_speech_worker(self):
        """Start background worker for non-blocking speech"""
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        log_debug("Speech worker thread started")

    def _speech_worker(self):
        """Background worker to process speech queue"""
        while True:
            try:
                # Get next speech item
                text, callback = self.speech_queue.get(timeout=1)
                
                # Speak it
                self._speak_blocking(text, callback)
                
                # Mark as done
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                log_error(f"Error in speech worker: {e}")

    def stop_speaking(self):
        """Stop current speech and clear queue"""
        try:
            if self.engine:
                self.engine.stop()
            
            # Clear queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except queue.Empty:
                    break
            
            self.is_speaking = False
            log_debug("Speech stopped and queue cleared")
            
        except Exception as e:
            log_error(f"Error stopping speech: {e}")

    def listen(self, timeout: Optional[int] = None, 
               phrase_time_limit: Optional[int] = None,
               show_progress: bool = True) -> str:
        """
        Listen for speech input
        
        Args:
            timeout: Seconds to wait for phrase start
            phrase_time_limit: Max seconds for phrase
            show_progress: Show listening progress
            
        Returns:
            str: Recognized text (empty string on failure)
        """
        config = ListenerConfig()
        timeout = timeout or config.timeout
        phrase_time_limit = phrase_time_limit or config.phrase_time_limit
        
        self.stats['total_listens'] += 1
        
        recognizer = sr.Recognizer()
        
        # Configure recognizer
        recognizer.energy_threshold = config.energy_threshold
        recognizer.dynamic_energy_threshold = config.dynamic_energy
        recognizer.pause_threshold = config.pause_threshold
        
        try:
            with sr.Microphone() as source:
                if show_progress:
                    print("🎤 Listening...")
                log_debug("Started listening for speech input")
                
                # Adjust for ambient noise
                if config.dynamic_energy:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    log_debug(f"Adjusted energy threshold to: {recognizer.energy_threshold}")
                
                # Listen for audio
                audio = recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                if show_progress:
                    print("🔄 Recognizing speech...")
                log_debug("Audio captured, starting recognition")
                
                # Recognize speech
                text = self._recognize_speech(recognizer, audio, config.language)
                
                if text:
                    self.stats['recognition_successes'] += 1
                    log_info(f"✓ Recognized: '{text}'")
                    return text
                else:
                    self.stats['recognition_failures'] += 1
                    return ""
                
        except sr.WaitTimeoutError:
            log_warning("Listening timed out - no speech detected")
            self.stats['recognition_failures'] += 1
            return ""
            
        except Exception as e:
            log_error(f"Unexpected error during listening: {e}")
            self.stats['recognition_failures'] += 1
            return ""

    def _recognize_speech(self, recognizer: sr.Recognizer, audio: sr.AudioData, 
                         language: str) -> str:
        """
        Recognize speech from audio data with multiple fallbacks
        
        Args:
            recognizer: Speech recognizer instance
            audio: Audio data to recognize
            language: Language code
            
        Returns:
            str: Recognized text or empty string
        """
        # Try Google Speech Recognition
        try:
            text = recognizer.recognize_google(audio, language=language)
            return text.lower()
        except sr.UnknownValueError:
            log_warning("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            log_error(f"Google Speech Recognition service error: {e}")
        except Exception as e:
            log_error(f"Error in Google recognition: {e}")
        
        # Try Sphinx (offline) as fallback
        try:
            text = recognizer.recognize_sphinx(audio)
            log_info("Used Sphinx (offline) recognition as fallback")
            return text.lower()
        except sr.UnknownValueError:
            log_warning("Sphinx could not understand audio")
        except sr.RequestError as e:
            log_error(f"Sphinx error: {e}")
        except Exception:
            pass  # Sphinx not available
        
        return ""

    def listen_continuously(self, callback: Callable[[str], None], 
                          stop_event: Optional[threading.Event] = None):
        """
        Listen continuously and call callback with recognized text
        
        Args:
            callback: Function to call with recognized text
            stop_event: Event to signal stop
        """
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        log_info("Started continuous listening mode")
        
        def audio_callback(recognizer, audio):
            try:
                text = self._recognize_speech(recognizer, audio, "en-US")
                if text:
                    callback(text)
            except Exception as e:
                log_error(f"Error in continuous listening callback: {e}")
        
        # Start background listening
        stop_listening = recognizer.listen_in_background(microphone, audio_callback)
        
        # Wait for stop event
        if stop_event:
            stop_event.wait()
        
        # Stop listening
        stop_listening(wait_for_stop=False)
        log_info("Stopped continuous listening mode")

    def set_voice(self, voice_type: VoiceType):
        """Change voice type"""
        try:
            self.config.voice_type = voice_type
            voices = self.engine.getProperty('voices')
            
            if voices and voice_type.value < len(voices):
                self.engine.setProperty('voice', voices[voice_type.value].id)
                log_info(f"Voice changed to: {voices[voice_type.value].name}")
                return True
            
        except Exception as e:
            log_error(f"Error changing voice: {e}")
        
        return False

    def set_rate(self, rate: int):
        """Change speech rate (50-300 WPM)"""
        try:
            rate = max(50, min(300, rate))  # Clamp to valid range
            self.config.rate = rate
            self.engine.setProperty('rate', rate)
            log_info(f"Speech rate set to: {rate} WPM")
            return True
        except Exception as e:
            log_error(f"Error setting rate: {e}")
            return False

    def set_volume(self, volume: float):
        """Change volume (0.0-1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to valid range
            self.config.volume = volume
            self.engine.setProperty('volume', volume)
            log_info(f"Volume set to: {volume:.2%}")
            return True
        except Exception as e:
            log_error(f"Error setting volume: {e}")
            return False

    def get_available_voices(self) -> List[dict]:
        """Get list of available voices"""
        try:
            voices = self.engine.getProperty('voices')
            return [
                {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                }
                for voice in voices
            ]
        except Exception as e:
            log_error(f"Error getting voices: {e}")
            return []

    def get_stats(self) -> dict:
        """Get speech engine statistics"""
        success_rate = 0.0
        if self.stats['total_listens'] > 0:
            success_rate = (self.stats['recognition_successes'] / 
                          self.stats['total_listens'] * 100)
        
        return {
            **self.stats,
            'recognition_success_rate': f"{success_rate:.1f}%",
            'is_speaking': self.is_speaking,
            'queue_size': self.speech_queue.qsize() if self.speech_queue else 0
        }

    def cleanup(self):
        """Cleanup speech engine resources"""
        try:
            self.stop_speaking()
            
            if self.engine:
                self.engine.stop()
            
            log_info("Speech engine cleaned up")
            
        except Exception as e:
            log_error(f"Error during cleanup: {e}")


# Convenience function for quick text-to-speech
def quick_speak(text: str):
    """Quick speak without creating engine instance"""
    engine = SpeechEngine(SpeechConfig(mode=SpeechEngineMode.BLOCKING))
    engine.speak(text)
    engine.cleanup()


# Convenience function for quick speech recognition
def quick_listen(timeout: int = 5) -> str:
    """Quick listen without creating engine instance"""
    engine = SpeechEngine()
    result = engine.listen(timeout=timeout)
    engine.cleanup()
    return result