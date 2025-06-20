# utils/wake_word_detector.py

import pvporcupine
import pyaudio
import struct
import logging
from core.logger import log_info, log_error

class WakeWordDetector:
    def __init__(self, access_key, keyword_path):
        """
        Initializes the wake word detector.
        
        Args:
            access_key (str): Picovoice AccessKey for Porcupine
            keyword_path (str): Path to .ppn wake word model file
        """
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.is_listening = False
        self.detected = False

    def start(self, callback=None):
        """
        Starts listening for the wake word.
        
        Args:
            callback (function): Optional function to call when wake word is detected
        """
        try:
            log_info("Initializing Porcupine wake word engine...")
            self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])
            log_info(f"Loaded wake word model: {self.keyword_path}")

            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                format=pyaudio.paInt16,
                channels=1,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            log_info("Listening for wake word...")
            print("Listening for wake word...")

            self.is_listening = True
            while self.is_listening:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                result = self.porcupine.process(pcm)

                if result >= 0:
                    log_info("Wake word detected!")
                    print("Wake word detected!")
                    self.detected = True
                    if callback:
                        callback()
                    self.stop()

        except Exception as e:
            error_msg = f"Wake word detection error: {e}"
            log_error(error_msg)
            self.stop()

    def stop(self):
        """Stops the wake word detection."""
        self.is_listening = False
        log_info("Stopping wake word detector...")

        if self.audio_stream:
            self.audio_stream.close()
            self.audio_stream = None

        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None

        if self.pa:
            self.pa.terminate()
            self.pa = None

        log_info("Wake word detector stopped.")

    def is_wake_word_detected(self):
        """Returns True if wake word was detected."""
        return self.detected