import numpy as np
import librosa 
import math  # log


class Sound:
    def __init__(self, waveform=None, fs=None, path=None):
        if path is not None:
            self.load(path)
        elif waveform is not None and fs is not None:
            self.y = waveform
            self.fs = fs
        else:
            raise TypeError("Must provide either a waveform + sampling rate or a file path")
        
        self.f0 = self.estimate_f0()
        self.duration = len(self.y) / self.fs
    
    def pitch_shift_to(self, target_freq: float):
        """ Changes the pitch of a sound while maintaining its duration

        Args:
            freq (float): The desired frequency to tune the sound to

        Returns:
            ndarray: The new sound array, sampled at self.fs
        """
        num_steps = Sound.steps_between_freqs(self.f0, target_freq)
        return librosa.effects.pitch_shift(self.y, self.fs, num_steps)

    def stretch(self, rate):
        """ Changes the speed of the sound while maintaining its pitch

        Args:
            rate (float): The rate to speed or slow the sound with

        Returns:
            ndarray: The new sound array, sampled at self.fs
        """
        return Sound.time_stretch(self.y, rate)

    def estimate_f0(self):
        fund_freqs, _, _ = librosa.pyin(self.y, sr=self.fs, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        fund_freqs = fund_freqs[~np.isnan(fund_freqs)]
        return np.mean(fund_freqs)

    def load(self, path):
        self.y, self.fs = librosa.load(path)

    @staticmethod
    def steps_between_freqs(f1,f2):
        """ The number of steps required to go from f1 to f2 """
        get_step = lambda f: math.log(f/440, 2 ** (1/12))
        return get_step(f2) - get_step(f1)

    @staticmethod
    def time_stretch(y,rate):
        return librosa.effects.time_stretch(y, rate)

    def __str__(self):
        return f"This sound is {len(self.y)/self.fs:.2f}s long with a f0 of {self.f0:.1f} Hz"

