import pygame
import pygame.gfxdraw
from stream import FrequencyStream, ToneStream
import numpy as np


class ToneCollector:
    def __init__(self, notes, background=(127,127,127)):
        pygame.init()

        # GUI Initialization
        self.sysfont = pygame.font.SysFont(None, 48)
        self.sysfont_small = pygame.font.SysFont(None, 30)
        self.screen = pygame.display.set_mode((500, 500))
        self.background = background

        # Audio Initialization
        self.freqstream = FrequencyStream()
        self.tonestream = ToneStream()


        # Preferences & configuration
        self.fps = 60
        self.tone_duration = 1.5  # Seconds to play the tone for after user input
        self.recording_duration = 2  # How many seconds to record

        # Text colors
        self.good_color = (100,255,50)
        self.bad_color = None#(255,100,50)
        self.default_color = (0,0,0)

        # Control variables
        self.notes = notes


        # Control logic
        self.target_freq = 440
        self.freq_tol = 0.02  # target bandwidth to the left or right

        self.input_hist = []
        self.window_len = self.fps / 5  # Average past 5 f0's

        self.tone_recordings = dict()


    def go(self):
        self.freqstream.start()
        try:
            total_frame_time = int(1000/self.fps)
            while True:
                loop_start = pygame.time.get_ticks()

                # Handle input
                if self._handle_input() == False:
                    break
                
                # Process
                self.input_hist.append(self.freqstream.f0)
                self.input_hist = self.input_hist[-5:]
                input_freq = np.mean(self.input_hist)

                # Check if the person's in the target range
                in_target = False
                lower,upper= self.target_freq * (1-self.freq_tol), self.target_freq *(1+self.freq_tol)
                if lower < input_freq < upper:
                    in_target = True
                    #TODO: Note recording logic

                # Main draw loop
                self._draw(input_freq, in_target)

                # Sleep until next frame
                processing_time = pygame.time.get_ticks() - loop_start
                sleep_time = max(total_frame_time - processing_time, 0)
                pygame.time.wait(sleep_time)
        finally:
            self.close()


    def close(self):
        print("Stopping...")
        self.tonestream.stop()
        self.freqstream.stop()
        pygame.quit()


    # ####### #
    # Drawing # # # # # # # # # # # # # # # # # # # # # # # # #
    # ####### #

    def _draw(self, input_freq, freq_match):
        self.screen.fill(self.background)
        self._draw_gui()

        you_col = self.good_color if freq_match else None
        self._draw_text(f'You: {input_freq:.0f} Hz', (160,50), color=you_col)
        self._draw_text(f'Target: {self.target_freq} Hz', (140,80), (255,50,50))

        self._draw_text(f'Press SPACE to play the target tone', (0,400), font=self.sysfont_small)
        self._draw_text(f'Press Q to quit', (0,430), font=self.sysfont_small)
        

        pygame.display.update()

    def _draw_text(self, text, loc, color=None, font=None):
        if font is None:
            font = self.sysfont
        if color is None:
            color = self.default_color

        img = font.render(text, True, color)
        self.screen.blit(img, loc)

    def _draw_gui(self):
        
        pass

    # ##### #
    # Input # # # # # # # # # # # # # # # # # # # # # # # # # #
    # ##### #

    def _handle_input(self):
        event = pygame.event.poll()

        if event.type == pygame.QUIT:
            return False

        # Keyboard input
        if event.type == pygame.KEYDOWN:
            if event.unicode == ' ':
                self._play_tone()
            if event.unicode == 'q':
                return False
        
        
        return True
    

    def _play_tone(self):
        self.tonestream.play(self.target_freq, self.tone_duration, blocking=True)
