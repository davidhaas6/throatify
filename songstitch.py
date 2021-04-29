#%%
from effects import Sound
import numpy as np
import pandas as pd
import pretty_midi

# takes in sound and midi and outputs a SONDified midi song
class SongSticher:
	def __init__(self, midi_path, sound):
		self.song_df = self.extract_song_data(midi_path)
		self.sound = sound

	def extract_song_data(self, midi_path):
		# Read MIDI and extract instrument
		midi_data = pretty_midi.PrettyMIDI(midi_path)
		mapping_instrument = midi_data.instruments[0]  # instrument to map the sounds to	

		# Form an array of the song parameters in question
		attrs = ['start', 'end', 'pitch', 'velocity']
		song_data = [[getattr(note, a) for a in attrs] for note in mapping_instrument.notes]	

		# Turn that array into a dataframe
		song_df = pd.DataFrame(song_data, columns=['start','end','note', 'velocity'])		

		# Extract frequency information
		to_hz = lambda notenum: 2 ** ((notenum - 69)/12) * 440
		song_df['freq'] = song_df.note.map(to_hz)		

		# Calculate note duration
		song_df['duration'] = song_df.end - song_df.start
		song_df['round_duration'] = song_df.duration.apply(lambda v: np.round(v, 2))
		
		return song_df

	def map_sound(self):
		# create empty samples array for the output song
		song_length = self.song_df.end.iloc[-1]
		total_samples = int(np.ceil(song_length * self.sound.fs))
		out_song = np.zeros((total_samples,), dtype=self.sound.y.dtype)

		# generate a sound for each pitch/duration note present in the song
		freq_groups = self.song_df.groupby(by=['freq'])['round_duration']

		sounds = dict()
		for freq,durations in freq_groups:
			# generate the base pitch shifted
			freq_shifted = self.sound.pitch_shift_to(freq)
			for t in set(durations):
				# Generate a sound for each duration present at that pitch
				rate = self.sound.duration / t
				sounds[(freq,t)] = Sound.time_stretch(freq_shifted, rate)

		# place each sound into the output array, corresponding with the notes
		for _,row in self.song_df.iterrows():
			# Gather note data and get the sound 
			cur_sound = sounds[(row['freq'], row['round_duration'])]
			start_sample = int(row['start'] * self.sound.fs)
			end_sample = start_sample + len(cur_sound)

			# Place it in the output
			out_song[start_sample:end_sample] += cur_sound

		return out_song


#%%
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "mee.wav")
sound = Sound(path=file_path)

ss = SongSticher('songs/mii_channel.mid', sound)
ss.song_df
#%% empty array
length = ss.song_df.end.iloc[-1] + 3 # Song length in seconds + padding
total_samples = int(np.ceil(length * sound.fs))
out_song = np.zeros((total_samples,),dtype=sound.y.dtype)


#%% collect sound types
from tqdm import tqdm
freq_groups = ss.song_df.groupby(by=['freq'])['round_duration']

sounds = dict()
for freq,durations in tqdm(freq_groups):
	# generate a sound for each frequency/duration combo
	freq_shifted = sound.pitch_shift_to(freq)
	for t in set(durations):
		rate = sound.duration / t
		sounds[(freq,t)] = Sound.time_stretch(freq_shifted, rate)

# %%

for _,row in ss.song_df.iterrows():
	start_sample = int(row['start'] * sound.fs)
	cur_sound = sounds[(row['freq'], row['round_duration'])]
	end_sample = start_sample + len(cur_sound)
	# print(start_sample,end_sample,row['start'],row['round_duration'], len(cur_sound)/sound.fs)
	out_song[start_sample:end_sample] += cur_sound


# %%
import sounddevice as sd
sd.play(out_song[:sound.fs*15], sound.fs)


# %%
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "mee.wav")
sound = Sound(path=file_path)

sticher = SongSticher('songs/toto_africa.mid', sound)
sitched_song = sticher.map_sound()

import sounddevice as sd
sd.play(sitched_song[:sound.fs*15], sound.fs)
print("done")
# %%