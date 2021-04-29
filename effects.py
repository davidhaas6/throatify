import numpy as np
import librosa 
import math  # log


class Sound:
    def __init__(self, waveform=None, fs=None, path=None, trim=True, f0=True):
        if path is not None:
            self.load(path)
        elif waveform is not None and fs is not None:
            self.y = waveform
            self.fs = fs
        else:
            raise TypeError("Must provide either a waveform + sampling rate or a file path")

        if trim: self.y = librosa.effects.trim(self.y)[0]
        self.f0 = self.estimate_f0() if f0 else None

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

    @staticmethod
    def time_extend(y, fs, new_duration: float):
        """ Loops and cuts an audio track so it lasts `new_duration` seconds

        Args:
            y (ndarray): audio
            fs (float): sampling rate
            new_duration (float): number of seconds to fit sound into

        Returns:
            ndarray: extended sound array
        """
        additional_samples = int(new_duration * fs)  # total amount of samples to add onto the track

        repeats = additional_samples // len(y)  # number of times to repeat the whole track
        tail_samples = additional_samples % len(y) # number of samples to tail on at the end

        # extended = np.hstack( (y, np.zeros((additonal_samples,))) )
        extended = np.tile(y, repeats)
        extended = np.hstack( (extended, y[:tail_samples]) )

        return extended
        # while additional_samples - len(y) > 0:

    @staticmethod
    def sample_cut_loop(y, num_samples):
        repeats = num_samples // len(y)  # number of times to repeat the whole track
        tail_samples = num_samples % len(y) # number of samples to tail on at the end

        # extended = np.hstack( (y, np.zeros((additonal_samples,))) )
        extended = np.tile(y, repeats)
        extended = np.hstack( (extended, y[:tail_samples]) )

        # keep track of the indexes too
        y_idx = np.arange(len(y))
        extended_idx = np.tile(y_idx, repeats)
        extended_idx = np.hstack( (extended_idx, y_idx[:tail_samples]) )

        return extended, extended_idx

    def __str__(self):
        return f"This sound is {len(self.y)/self.fs:.2f}s long with a f0 of {self.f0:.1f} Hz"

