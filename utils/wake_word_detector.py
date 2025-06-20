# utils/wake_word_detector.py

import pvporcupine
import pyaudio
import struct

class WakeWordDetector:
    def __init__(self, access_key, keyword_path):
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.pa = None
        self.audio_stream = None

    def start(self):
        self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            format=pyaudio.paInt16,
            channels=1,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

        print("Listening for wake word...")
        while True:
            pcm = self.audio_stream.read(self.porcupine.frame_length)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm)
            if result >= 0:
                print("Wake word detected!")
                return True

    def stop(self):
        if self.porcupine:
            self.porcupine.delete()
        if self.audio_stream:
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()