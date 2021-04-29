#%%
import numpy as np
import librosa 
import math  # log
from effects import Sound

#%%
import sounddevice as sd  # https://gist.github.com/akey7/94ff0b4a4caf70b98f0135c1cd79aff3
import time
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "mee.wav")
sound = Sound(path=file_path)
print(sound)
sd.play(sound.y, sound.fs)
#%% Absolute step shifts

notes = ['g4', 'A4', 'b4']
sounds = [sound.pitch_shift_to(note) for note in notes]

# music = [2,1,0,2,1,0,0,0,0,1,1,1,2,1,0]
music = [2,1,0]
song = [sounds[n] for n in music]
#%%


for t in song:
    # stream.stop_stream()
    sd.play(t, sound.fs)
    time.sleep(len(t)/sound.fs)
sd.stop()

# %%
stretched = sound.stretch(0.5)
sd.play(stretched, sound.fs)
time.sleep(len(stretched)/sound.fs)
sd.stop()

# %%
