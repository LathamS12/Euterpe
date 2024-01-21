import random

class Database:
    def __init__(self):   
        self.NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                            'F#', 'G', 'G#', 'A','A#', 'B']

        self.intervals = [
            'minor 2nd', 'major 2nd',
            'minor 3rd', 'major 3rd', 
            'perfect 4th', 'tritone', 'perfect 5th',
            'minor 6th', 'major 6th',
            'minor 7th', 'major 7th',
            'octave'
            ]
        self.interval_dict = dict(zip(range(1, 13), self.intervals))

        self.chord_formulas = {
                'major' : [12, 4, 7],
                'minor' : [12, 3, 7],
                'diminished' : [12, 3, 6],
                'augmented' : [12, 4, 8],
                'sus2': [12, 2, 7],
                'sus4' : [12, 5, 7],
                'major 6th' : [12, 4, 7, 9],
                'minor 6th' : [12, 3, 7, 9],
                'major 7th' : [12, 4, 7, 11],
                'minor 7th' : [12, 3, 7, 10],
                'dominant 7th' : [12, 4, 7, 10],
                'maj 7th shell' : [12, 4, 11],
                'min 7th shell' : [12, 3, 10],
                'dom 7th shell' : [12, 4, 10],
                'diminished 7th' : [12, 3, 6, 9],
                'half dim. 7th' : [12, 3, 6, 10],
                'augmented 7th' : [12, 4, 8, 10]
            }
    
        self.intervals_by_key = self._build_intervals_by_key()
        self.midi_to_ansi = self._midi_to_ansi_converter()  
        self.chord_dict = self._build_chord_dict()  
    
    def _midi_to_ansi_converter(self):
        midi_to_ansi = {}
        octave = 0
        for val in range(12,109):
            note_pos = val % 12 
            name = f'{self.NOTE_NAMES[note_pos]}{octave}'
            midi_to_ansi[val] = name
        
            if note_pos==11:
                octave +=1

        return midi_to_ansi

    def _build_intervals_by_key(self):
        NOTES_COPY = self.NOTE_NAMES.copy()

        intervals = {}
        for note in self.NOTE_NAMES:  
            temp_dict = {} 
            for i, n in enumerate(move_first_to_end(NOTES_COPY)):
                temp_dict[i+1] = n

            intervals[note] = temp_dict
        return intervals

    def _build_chord_dict(self):  
        chord_database = {}
        for chord_type, pattern in self.chord_formulas.items():
            next = self._get_chord_in_all_keys(chord_type, pattern)
            chord_database.update(next)

        return chord_database
    
    def _get_chord_in_all_keys(self, chord_name, pattern):
        chord_dict = {}
        for key in self.NOTE_NAMES:    
            chord = []
            for note in pattern:
                chord.append(self.intervals_by_key[key][note])
            chord_dict[' '.join(chord)] = f'{key} {chord_name}'     
        return chord_dict     
 
    def get_note_name(self, val):
        return self.midi_to_ansi[val]
    
    def get_note_k12(self, val):
        return self.get_note_name(val)[:-1]
    
    def calculate_intervals(self, val_list):
        intervals = []
        for i in range(len(val_list)-1):
            diff = val_list[i+1] - val_list[i]
            intervals.append(diff)    
        return intervals

    def get_interval_names(self, interval_list):
        name_list = []

        for interval in interval_list:    
            octaves, remainder = divmod(interval, 12)

            if octaves == 0:
                p1 = ''
            elif octaves == 1:
                p1 = f'{octaves} octave' 
            else:    
                p1 = f'{octaves} octaves'

            if remainder == 0:
                p2 = ''
            else:
                p2 = f'{self.interval_dict[remainder]}'
    
            if len(p1) > 0 and len(p2) > 0:
                name = f'{p1} + {p2}'
            else:
                name = f'{p1}{p2}' 

            name_list.append(name)

        return name_list
     
    #quiz mode
    def get_interval_question(self, key='All'):
        if key == 'All':
            root = random.choice(self.NOTE_NAMES)
        else:
            root = key

        random_interval = random.choice(range(1, 13))
        interval_name = self.interval_dict[random_interval]
        answer = self.intervals_by_key[root][random_interval]
        return [root, interval_name, answer]

    def get_chord_question(self, key='All'):
        chord_list = 'diatonic major'
        chord_list = 'diatonic 7th'
        chord_list = 'all'

        if key == 'All':
            root = random.choice(self.NOTE_NAMES)
        else:
            root = key

        chord_name, answer = random.choice(list(self.chord_dict.items()))
        return chord_name, answer
       
class Piano:
    def __init__(self):
        self.key_status = dict(zip(list(range(21,109)), [0]*88))
        self.db = Database()
    
    def press_multi(self, *keys): # Used for testing
        for key in keys:
            self.key_status[key]=1
    
    def key_reset(self):
        for key in self.key_status.keys():
            self.key_status[key] = 0 

    def get_pressed_key_vals(self):
        return sorted([k for k, v in self.key_status.items() if v==1])
        
    def get_pressed_key_names(self):
        key_vals = self.get_pressed_key_vals()
        return [self.db.get_note_name(val) for val in key_vals]
    
    def get_pressed_k12(self):
        keys = self.get_pressed_key_names()
        return [k[:-1] for k in keys]

    def get_pressed_intervals(self):
        pressed_keys = self.get_pressed_key_vals()
        interval_values = self.db.calculate_intervals(pressed_keys)
        interval_names = self.db.get_interval_names(interval_values)
        return interval_names

    def get_pressed_chord(self):
        pressed_keys = self.get_pressed_key_vals()
        
        chord_tones = []
        for key in pressed_keys:
            tone = self.db.get_note_k12(key)
            chord_tones.append(tone)

        no_dupes = set(chord_tones)
        
        matches = [k for k, v in self.db.chord_dict.items() 
                            if no_dupes == set(k.split())]
        if matches:
            if len(matches)>1:
                print('Warning: Multiple chords detected')

            final = self._check_for_inversions(matches[0])
            return final
        
        
    def _check_for_inversions(self, chord_spelling):
        pressed_keys = self.get_pressed_key_vals()
        bass_note = self.db.get_note_k12(pressed_keys[0])

        chord_name = self.db.chord_dict[chord_spelling]
        chord_notes = chord_spelling.split()

        if bass_note==chord_notes[0]:
            pass
        elif bass_note==chord_notes[1]:
            chord_name += ' (1st)'
        elif bass_note==chord_notes[2]:
            chord_name += ' (2nd)'
        elif chord_notes[3]:
            if bass_note==chord_notes[3]:
                chord_name += ' (3rd)'

        return chord_name
    

#Utility functions
def move_first_to_end(input_list):
    first_item = input_list.pop(0)
    input_list.append(first_item)
    return input_list




