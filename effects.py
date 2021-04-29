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
            self.f0 = self.estimate_f0()
        else:
            raise AttributeError("Must provide either a waveform and sampling rate or a file path")
    
    def pitch_shift_to(self, note: str):
        target_freq = librosa.note_to_hz(note)
        num_steps = Sound.steps_between_freqs(self.f0, target_freq)
        return librosa.effects.pitch_shift(self.y, self.fs, num_steps)

    def estimate_f0(self):
        fund_freqs, _, _ = librosa.pyin(self.y, sr=self.fs, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        fund_freqs = fund_freqs[~np.isnan(fund_freqs)]
        return np.mean(fund_freqs)

    def load(self, path):
        self.y, self.fs = librosa.load(path)
        self.f0 = self.estimate_f0()

    @staticmethod
    def steps_between_freqs(f1,f2):
        """ The number of steps required to go from f1 to f2 """
        get_step = lambda f: math.log(f/440, 2 ** (1/12))
        return get_step(f2) - get_step(f1)

    def __str__(self):
        return f"This sound is {len(self.y)/self.fs:.2f}s long with a f0 of {self.f0:.1f} Hz"

