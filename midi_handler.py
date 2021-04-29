import pretty_midi
import pandas as pd

class MidiExtractor:
    def __init__(self, path):
        midi_data = pretty_midi.PrettyMIDI(path)
        instruments = midi_data.instruments
        piano1 = instruments[0]

        self.song_df = pd.DataFrame(MidiExtractor._get_raw_notes(piano1), 
                columns=['start','end','note', 'velocity'])
        to_hz = lambda notenum: 2 ** ((notenum - 69)/12) * 440
        self.song_df['freq'] = piano_df.note.map(to_hz)
        self.song_df['duration'] = piano_df.end - piano_df.start

    @staticmethod
    def _get_raw_notes(instrument):
        attrs = ['start', 'end', 'pitch', 'velocity']
        return [[getattr(note, a) for a in attrs] for note in instrument.notes]

    