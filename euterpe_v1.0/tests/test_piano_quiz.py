import sys
sys.path.append('C:/Users/Scott/Dropbox/Data Science/Portfolio/piano_quiz_v1/modules')

import unittest
from unittest.mock import MagicMock

import piano_quiz_v1 as pq
import music_v1 as music

import pygame
import pygame.midi
import pandas as pd


class Test_Streaming_Setup(unittest.TestCase):
    def setUp(self):
        pq.init_pygame()
        self.input_id = pygame.midi.get_default_input_id() 
        # I don't set up the MIDI stream here because errors 
        # in setup don't count as failed tests.

    def test_input_available(self):  
        self.assertEqual(self.input_id, 1, msg = 'No input available')

    def test_midi_streaming(self):
        input = pygame.midi.Input(self.input_id)

        going = True
        while(going):
            if input.poll()==True:
                going=False

        self.assertEqual(input.poll(), True)

    def test_post_midi_as_pygame(self):
        input = pygame.midi.Input(self.input_id)

        going = True
        while(going):
            if input.poll()==True:
                pygame_events = pq.post_midi_as_pygame(input)
                going = False

        self.assertIsInstance(pygame_events[0], pygame.event.Event)

    def tearDown(self):
        pq.close_midi_stream()
        pygame.quit()

class Test_Free_Play(unittest.TestCase):
    def setUp(self):
        self.game = pq.Game()
        self.screen = self.game.gui.screen

    #def test_single_note_mode(self):    
    #   self.game._single_note_mode([60], self.screen)

    def tearDown(self):
       pass

class Test_Game_Functions(unittest.TestCase):

    def setUpClass(self):
        self.game = pq.Game()
        self.mock_event = MagicMock()
        self.mock_event.__dict__ = {'data1': 60} 
        
    def test_get_note_val(self):
        val = pq.get_note_val(self.mock_event)
        self.assertEqual(val, 60)
    
    def test_handle_no_event(self):
        self.game.game_event_handler()
        piano = music.Piano()
        no_event = MagicMock()
        no_event.__dict__ = {'data1': 0} 

    def test_move_around_game(self):
        self.game = pq.Game()
        pass

    def test_event_handler(self):
        pass

    def test_handle_midi_key_release(self):
        pass

    def test_handle_midi_key_press(self):
        pass

class Test_GUI(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.gui = pq.GUI()
        self.screen = self.gui.screen

    def test_screen(self):
        self.assertIsInstance(self.screen, pygame.surface.Surface)
    
    def test_draw_text_to_screen(self):
        white = (255, 255, 255)
        self.gui.draw_text_to_screen('text', 50, white, 70)
        #self.assertIsInstance(text, pygame.surface.Surface)

    def test_get_centered_xy(self):
        white = (255, 255, 255)
        test_surface = pygame.Surface((100, 300))

        xy = self.gui.get_centered_xy(test_surface)
        self.assertEqual(xy, [350, 150])

    def tearDown(self):
        pygame.quit()



class Test_Welcome_Screen(unittest.TestCase):
    def setUp(self):
        self.gui = pq.GUI()
        pygame.init()

        self.ASSET_FOLDER = pq.ASSET_FOLDER

    def test_screen_image_available(self):
        image = pygame.image.load(f'{self.ASSET_FOLDER}/welcome screen.png').convert()
        self.assertIsInstance(image, pygame.Surface)

if __name__ == '__main__':
    unittest.main()