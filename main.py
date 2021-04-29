import glob
from gui import ToneCollector

def main():
    # print("Welcome to Throatify! Please choose a song:")
    
    # songs = glob.glob('songs/*.mid')
    # for i, song in enumerate(songs):
    #     print(f'{i+1}. {song[song.find("/")+1:]}')
    # input('\nSong number: ')

    tones = ToneCollector([440])
    tones.go()  # Start GUI and collect tones
    recordings = tones.tone_recordings

if __name__ == "__main__":
    main()