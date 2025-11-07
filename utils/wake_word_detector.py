import struct
import pyaudio

from core.logger import loginfo, logerror


class WakeWordDetector:
    """
    Porcupine wake-word detector wrapper.
    """

    def __init__(self, access_key: str, keyword_path: str):
        """
        Initializes the wake word detector.

        Args:
            access_key (str): Picovoice AccessKey for Porcupine.
            keyword_path (str): Path to .ppn wake word model file.
        """
        self.access_key = access_key
        self.keyword_path = keyword_path

        self.porcupine = None
        self.pa = None
        self.audio_stream = None

        self.is_listening = False
        self._detected = False

    def start(self, callback=None):
        """
        Starts listening for the wake word.

        Args:
            callback (callable | None): Optional function to call when wake word is detected.
        """
        try:
            loginfo("Initializing Porcupine wake word engine...")
            try:
                # Import pvporcupine at runtime using importlib to avoid static analyzer unresolved-import errors.
                import importlib
                pvporcupine = importlib.import_module("pvporcupine")
            except Exception as ie:
                err = (
                    "Porcupine SDK (pvporcupine) is not installed. "
                    "Install it with 'pip install pvporcupine' and ensure it is available in the runtime."
                )
                logerror(f"{err} ({ie})")
                raise RuntimeError(err) from ie

            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keyword_paths=[self.keyword_path],
            )
            loginfo(f"Loaded wake word model: {self.keyword_path}")

            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                format=pyaudio.paInt16,
                channels=1,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )

            loginfo("Listening for wake word...")
            print("Listening for wake word...")
            self.is_listening = True

            while self.is_listening:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                result = self.porcupine.process(pcm)

                if result >= 0:
                    loginfo("Wake word detected!")
                    print("Wake word detected!")
                    self._detected = True
                    if callback:
                        try:
                            callback()
                        except Exception as cb_err:
                            logerror(f"Wake word callback failed: {cb_err}")
                    self.stop()
        except Exception as e:
            err = f"Wake word detection error: {e}"
            logerror(err)
            self.stop()

    def stop(self):
        """Stops the wake word detection and releases resources."""
        self.is_listening = False
        loginfo("Stopping wake word detector...")

        if self.audio_stream is not None:
            try:
                self.audio_stream.close()
            except Exception:
                pass
            self.audio_stream = None

        if self.porcupine is not None:
            try:
                self.porcupine.delete()
            except Exception:
                pass
            self.porcupine = None

        if self.pa is not None:
            try:
                self.pa.terminate()
            except Exception:
                pass
            self.pa = None

        loginfo("Wake word detector stopped.")

    def is_wake_word_detected(self) -> bool:
        """Returns True if wake word was detected."""
        return self._detected
