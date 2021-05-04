#%%
from effects import Sound
import numpy as np
import pandas as pd
import pretty_midi

# takes in sound and midi and outputs a SONDified midi song
# todo: add suport for possible: 
# 	mapping multiple sounds to mulitple instruments
#	different methods for splicing in sounds
#	joining instruments into one df
#	shifting keys

class SongSticher:
	def __init__(self, midi_path, sound, midi_instrument=0):
		self.song_df = self.extract_song_data(midi_path, midi_instrument)
		self.sound = sound

	def extract_song_data(self, midi_path, midi_instrument):
		# Read MIDI and extract instrument
		midi_data = pretty_midi.PrettyMIDI(midi_path)
		mapping_instrument = midi_data.instruments[midi_instrument]  # instrument to map the sounds to	

		# Form an array of the song parameters in question
		attrs = ['start', 'end', 'pitch', 'velocity']
		song_data = [[getattr(note, a) for a in attrs] for note in mapping_instrument.notes]	

		# Turn that array into a dataframe
		song_df = pd.DataFrame(song_data, columns=['start','end','note', 'velocity'])		

		# Extract frequency information
		key_shift = 0  # number of steps to shift notes by
		to_hz = lambda notenum: 2 ** ((notenum + key_shift - 69)/12) * 440
		song_df['freq'] = song_df.note.map(to_hz)		

		# Calculate note duration
		song_df['duration'] = song_df.end - song_df.start
		song_df['round_duration'] = song_df.duration.apply(lambda v: np.round(v, 2))
		
		return song_df

	# TODO: What if you did like a sliding pitch shift so each sound is the same length
	# 		instead of having short and fast versions of the sound. you could overlay multiple
	#		different copies too when there's >1 note playing at once.
	#		you could also still just calculate the shift K times for K different frequencies in the song.
	#		you just have to chop the sound in the right place and stitch it with a different freq sound.
	#		prolly a clever way to deal with rests too. like continuing from where you left off
	def map_sound(self):
		fs = self.sound.fs

		# create empty samples array for the output song
		song_length = self.song_df.end.iloc[-1] + 3
		total_samples = int(np.ceil(song_length * fs))
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
			if end_sample < len(out_song):
				out_song[start_sample:end_sample] += cur_sound
			else:
				# Adjust for sounds rolling over the total song length
				end_sample = len(out_song)
				out_song[start_sample:end_sample] += cur_sound[:end_sample-start_sample]
				break

		return out_song

	def map_sound_2(self):
		fs = self.sound.fs

		# create empty samples array for the output song
		song_length = self.song_df.end.iloc[-1] + 3
		total_samples = int(np.ceil(song_length * fs))
		out_song = np.zeros((total_samples,), dtype=self.sound.y.dtype)

		# keep track of the corresponding input sample index for each sample in the song
		in_sample_idx = np.zeros_like(out_song)
		in_sample_idx[:] = -1

		# generate a sound for each pitch/duration note present in the song
		sounds = dict()
		for freq in set(self.song_df.freq):
			sounds[freq] = self.sound.pitch_shift_to(freq)

		# place each sound into the output array, corresponding with the notes
		for _,row in self.song_df.iterrows():
			cur_sound = sounds[row['freq']]
			duration_samples = int(row['round_duration'] * fs)  # the number of samples this sound byte will fill

			out_start_sample = int(row['start'] * fs)
			out_end_sample = out_start_sample + duration_samples

			# Find the sample the last sound byte ended with
			prev_idxs = in_sample_idx[:out_start_sample+1]
			prev_idxs = prev_idxs[prev_idxs != -1]
			in_start_sample = int(prev_idxs[-1]) if len(prev_idxs) > 0 else 0

			chopped_end_sample = min(in_start_sample + duration_samples, len(cur_sound))

			# calculate needed length for this byte and extend if necessary
			chopped_len = chopped_end_sample - in_start_sample
			chopped_idxs = np.arange(in_start_sample, chopped_end_sample)
			chopped_sound = cur_sound[in_start_sample:chopped_end_sample]

			# form sound: the end sound that will be inserted into the output audio
			# form sound indicies: indicies for the samples of the `sound` so the next sound knows where to start from
			if duration_samples > chopped_len:
				additional_samples = duration_samples - chopped_len
				extended_sound, extended_idxs = Sound.sample_cut_loop(cur_sound, additional_samples)

				# append the extended sound and its indicies onto the chopped sound
				sound = np.hstack((chopped_sound, extended_sound))
				sound_idxs = np.hstack( (chopped_idxs, extended_idxs) )
			else:
				sound = chopped_sound
				sound_idxs = chopped_idxs

			# check to make sure we came out w/ the right duration
			if len(sound) != duration_samples: 
				print(len(sound),duration_samples, len(sound) - duration_samples)

			out_song[out_start_sample:out_end_sample] += sound
			in_sample_idx[out_start_sample:out_end_sample] = sound_idxs
			
		return out_song, in_sample_idx


# %%
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "sounds/mee.wav")
sound = Sound(path=file_path, trim=True)

ss = SongSticher('songs/mii_channel.mid', sound)

#%%
sitched_song = ss.map_sound()
# sitched_song,i = ss.map_sound_2()
idxs = pd.Series(i)
idxs[:sound.fs*3].plot()

print("song mapped")
#%%
idxs = pd.Series(i)
idxs[:sound.fs*3].plot(xlabel='out samples', ylabel='input sound samples')
# plt.xlabel('samples')
#%%
idxs = pd.Series(sitched_song)
idxs[:sound.fs*3].plot()
#%%
# import sounddevice as sd
# start, length = 0,30
# segment = sitched_song[sound.fs*start:sound.fs*(start+length)]
# sd.play(segment, sound.fs)
# import time
# time.sleep(length)
# print("done")

#%%

import soundfile as sf
sf.write('out/mii2.wav', sitched_song, sound.fs, subtype='PCM_24')
# %%


# TODO: what if you took it a step farther and approximated f0 for each window of a real mp3/song and then
#		tuned the audio to that window

# TODO: be able to select which instrument you want to map ur voice onto 
#		and map multiple voices to different instruments