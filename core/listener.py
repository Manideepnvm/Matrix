# core/listener.py

import threading
import queue
import time
from typing import Optional, List, Callable
from dataclasses import dataclass
from difflib import SequenceMatcher

from core.speech import SpeechEngine
from core.logger import log_info, log_error, log_debug


@dataclass
class WakeWordConfig:
    """Configuration for wake word detection"""
    primary_word: str = "hey matrix"
    alternative_words: List[str] = None
    sensitivity: float = 0.75  # Similarity threshold (0.0 to 1.0)
    timeout: int = 30  # Seconds before stopping continuous listening
    retry_on_failure: int = 3
    use_fuzzy_matching: bool = True
    
    def __post_init__(self):
        if self.alternative_words is None:
            self.alternative_words = [
                "matrix",
                "hey matrix",
                "ok matrix",
                "hi matrix"
            ]


class Listener:
    """Enhanced listener with advanced wake word detection and audio monitoring"""
    
    def __init__(self, wake_word: str = "hey matrix", config: Optional[WakeWordConfig] = None):
        self.config = config or WakeWordConfig(primary_word=wake_word)
        self.speech = SpeechEngine()
        
        # Wake word management
        self.wake_word = self.config.primary_word.lower()
        self.alternative_words = [w.lower() for w in self.config.alternative_words]
        
        # State management
        self.is_listening = False
        self.is_active = False
        self.last_detection_time = 0
        
        # Queue for async processing
        self.audio_queue = queue.Queue(maxsize=10)
        
        # Statistics
        self.stats = {
            'wake_word_detections': 0,
            'false_positives': 0,
            'total_phrases_heard': 0,
            'average_confidence': 0.0
        }
        
        # Callback
        self.on_wake_word_detected: Optional[Callable] = None
        
        log_info(f"Listener initialized with wake word: '{self.wake_word}'")

    def detect_wake_word(self, text: str) -> bool:
        """
        Detect wake word in text with fuzzy matching
        
        Args:
            text: Input text to check for wake word
            
        Returns:
            bool: True if wake word detected
        """
        if not text:
            return False
        
        text_lower = text.lower().strip()
        self.stats['total_phrases_heard'] += 1
        
        # Exact match check (fastest)
        if self._exact_match(text_lower):
            return self._handle_detection(text, 1.0)
        
        # Fuzzy match check (if enabled)
        if self.config.use_fuzzy_matching:
            confidence = self._fuzzy_match(text_lower)
            if confidence >= self.config.sensitivity:
                return self._handle_detection(text, confidence)
        
        return False

    def _exact_match(self, text: str) -> bool:
        """Check for exact wake word match"""
        # Check primary wake word
        if self.wake_word in text:
            return True
        
        # Check alternative wake words
        for alt_word in self.alternative_words:
            if alt_word in text:
                return True
        
        return False

    def _fuzzy_match(self, text: str) -> float:
        """
        Perform fuzzy matching for wake word detection
        
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        words_to_check = [self.wake_word] + self.alternative_words
        max_confidence = 0.0
        
        for wake_word in words_to_check:
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, text, wake_word).ratio()
            max_confidence = max(max_confidence, ratio)
            
            # Check if wake word appears as substring
            if wake_word in text:
                max_confidence = max(max_confidence, 0.9)
            
            # Check word-by-word matching
            text_words = text.split()
            wake_words = wake_word.split()
            
            if len(text_words) >= len(wake_words):
                for i in range(len(text_words) - len(wake_words) + 1):
                    window = " ".join(text_words[i:i + len(wake_words)])
                    window_ratio = SequenceMatcher(None, window, wake_word).ratio()
                    max_confidence = max(max_confidence, window_ratio)
        
        return max_confidence

    def _handle_detection(self, text: str, confidence: float) -> bool:
        """Handle wake word detection"""
        current_time = time.time()
        
        # Debounce: Ignore detections within 2 seconds
        if current_time - self.last_detection_time < 2.0:
            log_debug("Wake word detection debounced")
            return False
        
        self.last_detection_time = current_time
        self.stats['wake_word_detections'] += 1
        
        # Update average confidence
        total = self.stats['average_confidence'] * (self.stats['wake_word_detections'] - 1)
        self.stats['average_confidence'] = (total + confidence) / self.stats['wake_word_detections']
        
        log_info(f"Wake word detected with {confidence:.2%} confidence: '{text}'")
        
        # Trigger callback if set
        if self.on_wake_word_detected:
            try:
                self.on_wake_word_detected(text, confidence)
            except Exception as e:
                log_error(f"Error in wake word callback: {e}")
        
        return True

    def wait_for_wake_word(self, timeout: Optional[int] = None) -> Optional[str]:
        """
        Wait for wake word detection (blocking)
        
        Args:
            timeout: Maximum time to wait in seconds (None = infinite)
            
        Returns:
            str: Command text after wake word, or None if timeout
        """
        start_time = time.time()
        timeout = timeout or self.config.timeout
        
        log_info("Waiting for wake word...")
        self.is_listening = True
        
        retry_count = 0
        
        while self.is_listening:
            try:
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    log_info("Wake word detection timeout")
                    return None
                
                # Listen for audio
                query = self.speech.listen(timeout=5)
                
                if not query:
                    continue
                
                log_debug(f"Heard: '{query}'")
                
                # Check for wake word
                if self.detect_wake_word(query):
                    # Extract command after wake word
                    command = self._extract_command(query)
                    self.is_listening = False
                    return command
                
                retry_count = 0  # Reset retry counter on successful listen
                
            except Exception as e:
                log_error(f"Error in wake word detection: {e}")
                retry_count += 1
                
                if retry_count >= self.config.retry_on_failure:
                    log_error("Max retries reached in wake word detection")
                    return None
                
                time.sleep(0.5)
        
        return None

    def _extract_command(self, text: str) -> str:
        """
        Extract command text after wake word
        
        Args:
            text: Full text containing wake word
            
        Returns:
            str: Command portion of text
        """
        text_lower = text.lower()
        
        # Try to find and remove wake word
        for wake_word in [self.wake_word] + self.alternative_words:
            if wake_word in text_lower:
                # Find position and remove
                pos = text_lower.find(wake_word)
                if pos != -1:
                    command = text[pos + len(wake_word):].strip()
                    if command:
                        log_debug(f"Extracted command: '{command}'")
                        return command
        
        # If no command after wake word, return full text
        return text.strip()

    def start_continuous_listening(self, callback: Callable[[str], None]):
        """
        Start continuous listening in background thread
        
        Args:
            callback: Function to call when wake word detected
        """
        self.on_wake_word_detected = lambda text, conf: callback(self._extract_command(text))
        self.is_listening = True
        self.is_active = True
        
        thread = threading.Thread(target=self._continuous_listen_loop, daemon=True)
        thread.start()
        
        log_info("Started continuous listening mode")

    def _continuous_listen_loop(self):
        """Background loop for continuous listening"""
        while self.is_active:
            try:
                query = self.speech.listen(timeout=5)
                if query and self.detect_wake_word(query):
                    command = self._extract_command(query)
                    if self.on_wake_word_detected:
                        self.on_wake_word_detected(command, 1.0)
            except Exception as e:
                log_error(f"Error in continuous listening: {e}")
                time.sleep(1)

    def stop_listening(self):
        """Stop listening for wake word"""
        self.is_listening = False
        self.is_active = False
        log_info("Stopped listening")

    def set_wake_word(self, new_wake_word: str):
        """
        Change the wake word
        
        Args:
            new_wake_word: New wake word to use
        """
        old_word = self.wake_word
        self.wake_word = new_wake_word.lower()
        log_info(f"Wake word changed from '{old_word}' to '{self.wake_word}'")

    def add_alternative_word(self, alt_word: str):
        """
        Add an alternative wake word
        
        Args:
            alt_word: Alternative wake word to add
        """
        alt_word_lower = alt_word.lower()
        if alt_word_lower not in self.alternative_words:
            self.alternative_words.append(alt_word_lower)
            log_info(f"Added alternative wake word: '{alt_word}'")

    def get_stats(self) -> dict:
        """Get listener statistics"""
        return {
            **self.stats,
            'is_listening': self.is_listening,
            'is_active': self.is_active,
            'wake_word': self.wake_word,
            'alternative_words': self.alternative_words,
            'sensitivity': self.config.sensitivity
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'wake_word_detections': 0,
            'false_positives': 0,
            'total_phrases_heard': 0,
            'average_confidence': 0.0
        }
        log_info("Listener statistics reset")


# Backward compatibility
class LegacyListener(Listener):
    """Legacy listener for backward compatibility"""
    
    def __init__(self):
        super().__init__(wake_word="hey matrix")
        self.wake_word = "hey matrix"  # Exposed attribute for legacy code