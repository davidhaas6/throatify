import pyaudio
import numpy as np


class ToneStream:
    def __init__(self, volume=0.5, fs=44100, max_duration=60):
        self.audio = pyaudio.PyAudio()

        self.volume = volume
        self.fs = fs     # sampling rate, Hz, must be integer

        self.freq = None
        self.duration = None
        self.stream = None
        self.started = False


    def __del__(self):
        self.stop()


    def play(self, freq: float, duration: float, blocking=False):
        """Plays a non-blocking tone for a specified duration

        Args:
            freq (float): the frequency of the tone in hz
            duration (float): the duration of the tone in seconds
        """
        if self.started:
            return False

        self.freq = freq
        self.duration = duration

        callback = lambda *args: self._callback(*args)
        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.fs,
            output=True,
            stream_callback=callback,
            frames_per_buffer=int(duration * self.fs)
        )

        if blocking:
            start = time.time()
            while (time.time() - start) < self.duration:
                pass
        

    def stop(self):
        if self.stream is not None:
            # Close the stream
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None


    def _generate_samples(self, freq:float, duration:float, frames=False):
        w = 2 * np.pi * freq
        sample_length = duration if frames else self.fs*duration  # length in samples or seconds
        
        samples = (
            self.volume * np.sin(w/self.fs * np.arange(sample_length + 50))
        ).astype(np.float32).tobytes()

        return samples
                    

    def _callback(self, _, frame_count, time_info, flags):
        if not self.started:
            self.started = True
            print("Starting up!")
        else:
            self.started = False
            return None, pyaudio.paComplete
        
        samples = self._generate_samples(self.freq, frame_count, frames=True)

        return samples, pyaudio.paContinue


class FrequencyStream:
    def __init__(self, fft_rate=10, channels=1, samplerate=6000, format=pyaudio.paInt16):
        self.audio = pyaudio.PyAudio()

        # Audio parameters
        self.fs = samplerate # 44100 is industry standard
        self.FORMAT = format
        self.channels = channels
        self.chunk_size = int(self.fs / fft_rate) 

        self.stream = None
        self.stream_dt = np.dtype(np.int16).newbyteorder('<')
        
        self.f0 = -1


    def start(self):
        callback = lambda *args: self._callback(*args)
        self.stream = self.audio.open(format=self.FORMAT,
                                    channels=self.channels,
                                    rate=self.fs,
                                    input=True,
                                    stream_callback=callback,
                                    frames_per_buffer=self.chunk_size)
        return True


    def stop(self):
        self.stream.stop_stream()
        self.stream.close()


    def _fund_freq(self, x, npoints=2048):
        norm = (x-x.mean())/x.std()  # z-normalize the signal

        w = np.abs(np.fft.fft(norm, npoints))[1:]
        cycle_freqs = np.fft.fftfreq(npoints)[1:]

        real = cycle_freqs > 0
        hz = np.array([f * self.fs for f in cycle_freqs[real]])
        f0 = hz[np.argmax(w[real])]

        return f0


    def _callback(self, input_data, frame_count, time_info, flags):
        arr = np.frombuffer(input_data, dtype=self.stream_dt)
        self.f0 = self._fund_freq(arr)
        return input_data, pyaudio.paContinue


if __name__ == '__main__':
    import time
    
    if input('f for frequencystream, t for tonestream: ') == 'f':
        fstream = FrequencyStream()
        fstream.start()

        start = time.time()
        while (time.time() - start) < 10:
            print(f"f0 = {round(fstream.f0)}Hz")
            pass

        fstream.stop()

        print("Finished recording")
    else:
        tstream = ToneStream(max_duration=10)
        tstream.play(220, 3)

        start = time.time()
        while (time.time() - start) < 6:
            print(":I")
            time.sleep(.1)
            pass

        tstream.stop()
        print("Done!")