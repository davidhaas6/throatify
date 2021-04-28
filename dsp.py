import numpy as np

def speedx(sound_array, factor):
    """ Multiplies the sound's speed by some `factor` """
	# Create the upsampled/downsampled indicies over the sound array
    indices = np.round( np.arange(0, len(sound_array), factor).astype(int)

	# Sample the sound at the increased/decreased rate
	resampled_sound = sound_array[ indices ]

    return resampled_sound


def stretch(sound_array, f, window_size, h):
    """ Stretches the sound by a factor `f` 
	
	window_size: the length of overlapping parts
	h: hop length
	"""

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
        result[i2 : i2 + window_size] += (hanning_window*a2_rephased).astype(np.float64)

    result = ((2**(16-4)) * result/result.max()) # normalize (16bit)

    return result.astype('int16')


def pitchshift(snd_array, n, window_size=2**13, h=2**11):
    """ Changes the pitch of a sound by ``n`` semitones. """
    factor = 2**(1.0 * n / 12.0)

	# Inversely stretch the sound (before we shift) so it will maintain the same length
    stretched = stretch(snd_array, 1.0/factor, window_size, h)  

	# Change the speed to change the sound's frequency
	shifted = speedx(stretched[window_size:], factor)

    return shifted