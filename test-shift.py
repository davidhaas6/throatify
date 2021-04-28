#%%

import numpy as np

def speedx(sound_array, factor):
    """ Multiplies the sound's speed by some `factor` """
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[ indices.astype(int) ]


def stretch(sound_array, f, window_size, h):
    """ Stretches the sound by a factor `f` """

    phase  = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros( int( len(sound_array) /f + window_size))

    for i in np.arange(0, len(sound_array)-(window_size+h), h*f).astype(int):

        # two potentially overlapping subarrays
        a1 = sound_array[i: i + window_size]
        a2 = sound_array[i + h: i + window_size + h]

        # resynchronize the second array on the first
        s1 =  np.fft.fft(hanning_window * a1)
        s2 =  np.fft.fft(hanning_window * a2)
        phase = (phase + np.angle(s2/s1)) % 2*np.pi
        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))

        # add to result
        i2 = int(i/f)
        # print((hanning_window*a2_rephased).dtype)
        result[i2 : i2 + window_size] += (hanning_window*a2_rephased).astype(np.float64)

    result = ((2**(16-4)) * result/result.max()) # normalize (16bit)

    return result.astype('int16')


def pitchshift(snd_array, n, window_size=2**13, h=2**11):
    """ Changes the pitch of a sound by ``n`` semitones. """
    factor = 2**(1.0 * n / 12.0)
    stretched = stretch(snd_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)
    return stretched

#%%
from scipy.io import wavfile
import sounddevice as sd  # https://gist.github.com/akey7/94ff0b4a4caf70b98f0135c1cd79aff3
import time
import os
 
dir_path = os.path.dirname(os.path.realpath(__file__))

fs, waveform = wavfile.read(os.path.join(dir_path, "mee.wav"))
# sd.play(waveform, fs)

tones = [0,3,5]
transposed = [pitchshift(waveform, n) for n in tones]
#%%

for t in transposed:
    print(len(t))
    sd.play(t, fs)
    time.sleep(len(t)/fs * 0.8)
sd.stop()

# %%
