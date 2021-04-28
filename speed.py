#%%
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
        return f"This sound is {len(self.y)/fs:.2f}s long with a f0 of {self.f0:.1f} Hz"


#%%
import sounddevice as sd  # https://gist.github.com/akey7/94ff0b4a4caf70b98f0135c1cd79aff3
import time
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "whistle.wav")
sound = Sound(path=file_path)
print(sound)
#%% Absolute step shifts

notes = ['g4', 'A4', 'b4']
sounds = [sound.pitch_shift_to(note) for note in notes]

# music = [2,1,0,2,1,0,0,0,0,1,1,1,2,1,0]
music = [0,0,0,0,0,0,0,0]
song = [sounds[n] for n in music]
#%%

for t in song:
    sd.play(t, fs)
    time.sleep(len(t)/fs * 0.8)
sd.stop()

# %%
