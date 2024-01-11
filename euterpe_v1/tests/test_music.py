import sys
sys.path.append('C:/Users/Scott/Dropbox/Data Science/Portfolio/piano_quiz_v1/modules')

import unittest
from unittest.mock import MagicMock

import music_v1 as music

import pygame.midi


class Test_Piano_Functions(unittest.TestCase):    
    def setUp(self):
        self.piano = music.Piano()
  
    def test_create_piano(self):
        self.assertIsInstance(self.piano, music.Piano)

    def test_piano_init(self):
        pressed = sum(value==1 for value in self.piano.key_status.values())
        not_pressed = sum(value==0 for value in self.piano.key_status.values())
        self.assertEqual([pressed, not_pressed], [0, 88])
    
    def test_key_increment(self):
        self.piano.press_key(60)    
        self.assertEqual(self.piano.key_status[60], 1)

    def test_key_decrement(self):
        self.piano.key_status[60]=1
        self.piano.release_key(60)
        self.assertEqual(self.piano.key_status[60], 0)
    
    def test_press_multi(self):
        self.piano.press_multi(60, 64, 67)
        self.assertEqual([self.piano.key_status[x] for x in [60, 64, 67]], [1, 1, 1])

    def test_key_reset(self):
        self.piano.press_multi(60, 64, 47, 85, 27)
        self.piano.key_reset() 
        pressed = sum(value==1 for value in self.piano.key_status.values())
        self.assertEqual(pressed, 0)

    def test_get_pressed_key_vals(self):
        self.piano.press_multi(60, 64, 67)
        self.assertEqual(self.piano.get_pressed_key_vals(), [60, 64, 67])

    def test_get_pressed_key_names(self):
        self.piano.press_multi(60, 64, 67)
        self.assertEqual(self.piano.get_pressed_key_names(), ['C4', 'E4', 'G4'])
    
    def test_get_pressed_k12(self):
        self.piano.press_multi(60, 64, 67)
        self.assertEqual(self.piano.get_pressed_k12(), ['C', 'E', 'G'])

    def test_get_pressed_intervals(self):
        self.piano.press_multi(14, 16, 25, 72)
        correct_intervals = ['major 2nd', 
                             'major 6th', 
                             '3 octaves + major 7th']
        
        intervals = self.piano.get_pressed_intervals()

        self.assertEqual(intervals, correct_intervals)

    def test_get_interval_names(self):
        names = self.piano.db.get_interval_names([5, 10, 25])
        self.assertEqual(names, ['perfect 4th', 'minor 7th', '2 octaves + minor 2nd'])

    def test_get_pressed_chord(self):
        for x in [60, 64, 67]:
            self.piano.key_status[x]=1
        
        chord = self.piano.get_pressed_chord()
        self.assertEqual(chord, 'C major')


class Test_Music_functions(unittest.TestCase):    
    def setUp(self):
        self.db = music.Database()
        self.piano = music.Piano()

    def test_get_note_name(self):
        name_1 = self.db.get_note_name(60)
        name_2 = self.db.get_note_name(100)
        self.assertEqual([name_1, name_2], ['C4', 'E7'])

    def test_get_note_k12(self):
        k12_val_1 = self.db.get_note_k12(60)
        k12_val_2 = self.db.get_note_k12(100)
        self.assertEqual([k12_val_1, k12_val_2], ['C', 'E']) 

    def test_ansi_converter(self):
        note1 = self.db.midi_to_ansi[25]
        note2 = self.db.midi_to_ansi[60]
        note3 = self.db.midi_to_ansi[79]

        self.assertEqual([note1, note2, note3], ['C#1','C4', 'G5'])
    
    def test_calculate_intervals(self):
        key1 = 15
        key2 = 60
        key3 = 65

        intervals = self.db.calculate_intervals([key1, key2, key3])
        self.assertEqual(intervals, [45, 5])


    def test_intervals_by_key_dict(self):
        val1 = self.db.intervals_by_key['D'][7]
        val2 = self.db.intervals_by_key['F'][5]

        self.assertEqual([val1, val2], ['A', 'A#'])
   
    def test_build_chord_dict(self):
        val1 = self.db.chord_dict['C E G']
        self.assertEqual(val1, 'C major')

    def test_get_chord_in_all_keys(self):
        dict1 = self.db._get_chord_in_all_keys('major', [12, 4, 7])
        dict2 = self.db._get_chord_in_all_keys('dominant 7th', [12, 4, 7, 10])

        self.assertEqual([dict1['C E G'], dict2['F A C D#']],
                          ['C major', 'F dominant 7th'])
        

class Test_Identify_Chords(unittest.TestCase):
    def setUp(self):
        self.db = music.Database()
        self.piano = music.Piano() 

    def _single_chord_test(self, key_list, name):
        for key in key_list:
            self.piano.press_key(key) 
        chord = self.piano.get_pressed_chord()
        self.assertEqual(chord, name)


    def test_check_first_inversion(self):
        self.piano.press_multi(64, 67, 72)
        test = self.piano._check_for_inversions('C E G')
        self.assertEqual(test, 'C major (1st)')
    
    def test_check_second_inversion(self):
        self.piano.press_multi(67, 72, 75)
        test = self.piano._check_for_inversions('C D# G')
        self.assertEqual(test, 'C minor (2nd)')
    
    def test_check_third_inversion(self):
        self.piano.press_multi(58, 60, 64, 67)
        test = self.piano._check_for_inversions('C E G A#')
        self.assertEqual(test, 'C dominant 7th (3rd)')

    def test_major_chord(self):
        self._single_chord_test([60, 64, 67], 'C major')

    def test_minor_chord(self):
        self._single_chord_test([60, 63, 67], 'C minor')

    def test_diminished_chord(self):
        self._single_chord_test([60, 63, 66], 'C diminished')

    def test_augmented_chord(self):
        self._single_chord_test([60, 64, 68], 'C augmented')

    def test_sus2_chord(self):
        self._single_chord_test([60, 62, 67], 'C sus2')

    def test_maj6_chord(self):
        self._single_chord_test([60, 64, 67, 69], 'C major 6th') 

    def test_min6_chord(self):
        self._single_chord_test([60, 63, 67, 69], 'C minor 6th') 

    def test_maj7_chord(self):
        self._single_chord_test([60, 64, 67, 71], 'C major 7th')
    

                               
    def test_dom7_chord(self):
        self._single_chord_test([60, 64, 67, 70], 'C dominant 7th', )

    def test_maj7_shell_chord(self):
        self._single_chord_test([60, 64, 71], 'C maj 7th shell')

    def test_min7_shell_chord(self):
        self._single_chord_test([60, 63, 70], 'C min 7th shell')

    def test_dom7_shell_chord(self):
        self._single_chord_test([60, 64, 70], 'C dom 7th shell')

    def test_dim7_chord(self):
        self._single_chord_test([60, 63, 66, 69], 'C diminished 7th')
    


    def test_aug7_chord(self):
        self._single_chord_test([60, 64, 68, 70], 'C augmented 7th')


    def test_aug7_inversion(self):
        self._single_chord_test([64, 68, 70, 72], 'C augmented 7th (1st)')

    def test_maj7_inversion(self):
        self._single_chord_test([68, 72, 73, 77], 'C# major 7th (2nd)')


# Errors when a chord is identical to another chord's inversion
'''
    def test_sus4_chord(self):
        self._single_chord_test([60, 65, 67], 'C sus4')

    def test_halfdim7_chord(self):
        self._single_chord_test([60, 63, 66, 70], 'C half dim. 7th')

    def test_min7_chord(self):
        self._single_chord_test([60, 63, 67, 70], 'C minor 7th')
'''