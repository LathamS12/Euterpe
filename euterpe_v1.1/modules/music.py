import random

class Database:
    def __init__(self):   
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                            'F#', 'G', 'G#', 'A','A#', 'B']
        
        #self.note_names = ['C', 'D\u266D', 'D', 'E\u266D', 'E', 'F', 
        #                       'G\u266D', 'G', 'A\u266D', 'A','B\u266D', 'B']

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
            'dim' : [12, 3, 6],
            'aug' : [12, 4, 8],
            'sus2': [12, 2, 7],
            'sus4' : [12, 5, 7],
            'maj 6th' : [12, 4, 7, 9],
            'min 6th' : [12, 3, 7, 9],
            #'maj 6th shell' : [12, 4, 9],
            'min 6th shell' : [12, 3, 9],
            'maj 7th' : [12, 4, 7, 11],
            'min 7th' : [12, 3, 7, 10],
            'dom 7th' : [12, 4, 7, 10],
            'maj 7th shell' : [12, 4, 11],
            'min 7th shell' : [12, 3, 10],
            'dom 7th shell' : [12, 4, 10],
            'dim 7th' : [12, 3, 6, 9],
            'half dim 7th' : [12, 3, 6, 10],
            'aug 7th' : [12, 4, 8, 10],  
            'maj 9th' : [12, 2, 4, 7, 11],
            'maj 9th shell' : [12, 2, 4, 11],
            'min 9th' : [12, 2, 3, 7, 10],
            'min 9th shell' : [12, 2, 3, 10],
            'minor/major 7th' : [12, 3, 7, 11],
            'minor/major 7th shell' : [12, 3, 11],
            'add9' : [12, 2, 4, 7]
        }
         
    
        self.scale_formulas = {
            'major' : [12, 2, 4, 5, 7, 9, 11],
            'minor' : [12, 2, 3, 5, 7, 8, 10],
            'dorian' : [12, 2, 3, 5, 7, 9, 10],
            'phrygian' : [12, 1, 3, 5, 7, 8, 10],
            'lydian' : [12, 2, 4, 6, 7, 9, 11],
            'mixolydian' : [12, 2, 4, 5, 7, 9, 10],
            'aeolian' : [12, 2, 3, 5, 7, 8, 10],
            'locrian' : [12, 1, 3, 5, 6, 8, 10],
            'blues' : [12, 3, 5, 6, 7, 10],
            'harmonic minor' : [12, 2, 3, 5, 7, 8, 11],
            'melodic minor' : [12, 2, 3, 5, 7, 9, 11],
            'whole tone' : [12, 2, 4, 6, 8, 10],
            'pentatonic' : [12, 2, 4, 7, 9],
        }
        self.midi_to_ansi = self._midi_to_ansi_converter()  
        self.intervals_by_key = self._build_intervals_by_key()
        
        self.chords = self._build_chord_database() 

        self.major_and_minor_chords ={key: value for key, value in self.chords.items() 
                                        if ('major' in value or 'minor' in value) 
                                        and '/' not in value}
        
        self.seventh_chords ={key: value for key, value in self.chords.items() 
                                if ('maj 7th' in value or 'min 7th' in value
                                    or 'dom 7th' in value) 
                                    and 'shell' not in value}
        
        
        self.scales = self._build_scale_database()
        self.dia_maj, self.dia_7th = self._build_diatonic_chords()
    
    def _midi_to_ansi_converter(self):
        midi_to_ansi = {}
        octave = 0
        for val in range(12,109):
            note_pos = val % 12 
            name = f'{self.note_names[note_pos]}{octave}'
            midi_to_ansi[val] = name
        
            if note_pos==11:
                octave +=1

        return midi_to_ansi

    def _build_intervals_by_key(self):
        NOTES_COPY = self.note_names.copy()

        intervals = {}
        for note in self.note_names:  
            temp_dict = {} 
            for i, n in enumerate(self._move_first_to_end(NOTES_COPY)):
                temp_dict[i+1] = n

            intervals[note] = temp_dict
        return intervals

    def _move_first_to_end(self, input_list):
        first_item = input_list.pop(0)
        input_list.append(first_item)
        return input_list

    def _build_chord_database(self):  
        chord_database = {}
        for chord_type, formula in self.chord_formulas.items():
            dict = self._apply_pattern_in_all_keys(chord_type, formula)
            chord_database.update(dict)

            # Add inversions
            for chord_spelling in dict.keys():                
                #For some reason inversions of these types of chords not working
                if chord_type not in ['dim 7th', 'aug']:

                    inversion_list = self._get_inversions(chord_spelling)
                    for i, inversion in enumerate(inversion_list):
                        chord_database[inversion] = f"{chord_database[chord_spelling]} (inv {i+1})"

        return chord_database
    
    def _get_inversions(self, chord_spelling):
        inversions = []
        for i in range(1, len(chord_spelling.split())):
            inversion = " ".join(chord_spelling.split()[i:] + chord_spelling.split()[:i])
            inversions.append(inversion)
        return inversions

    def _build_scale_database(self):  
        scale_database = {}
        for scale_type, pattern in self.scale_formulas.items():
            next = self._apply_pattern_in_all_keys(scale_type, pattern)
            scale_database.update(next)
        
        reversed_db = {value: key.split() for key, value in scale_database.items()}

        return reversed_db
    
    def _apply_pattern_in_all_keys(self, pattern_name, pattern):
        dict = {}
        for root in self.note_names:    
            entry = []
            for note in pattern:
                entry.append(self.intervals_by_key[root][note])
            dict[' '.join(entry)] = f'{root} {pattern_name}'     
        return dict     

    def _build_diatonic_chords(self):
        pattern = 'major'
        major_scales = {key: value for key, value in self.scales.items() if pattern in key}

        diatonic_major_chords = {}
        diatonic_7th_chords = {}

        for name, scale in major_scales.items():
            chord_degrees = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']

            indices_maj = [0, 2, 4]
            indices_7th = [0, 2, 4, 6]

            chords_maj = {}
            chords_7th = {}
          
            for i in chord_degrees:    
                chord_maj = [scale[j%7] for j in indices_maj]
                chord_7th = [scale[j%7] for j in indices_7th]
                
                chords_maj[i] = chord_maj
                chords_7th[i] = chord_7th

                indices_maj = [x + 1 for x in indices_maj]
                indices_7th = [x + 1 for x in indices_7th]

            diatonic_major_chords[name] = chords_maj
            diatonic_7th_chords[name] = chords_7th

        return diatonic_major_chords, diatonic_7th_chords 


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
     

class Piano:
    def __init__(self):
        self.key_status = dict(zip(list(range(21,109)), [0]*88))
        self.db = Database()
    
    def press_multi(self, *keys): # Used for testing
        for key in keys:
            self.key_status[key]=1
    
    def key_reset(self):
        for key in self.key_status:
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
        
        matches = [k for k, v in self.db.chords.items() 
                            if no_dupes == set(k.split())]
        if matches:
            if len(matches)>1:
                print('Warning: Multiple chords detected')

            final = self._check_for_inversions(matches[0])
            return final
        
        
    def _check_for_inversions(self, chord_spelling):
        pressed_keys = self.get_pressed_key_vals()
        bass_note = self.db.get_note_k12(pressed_keys[0])

        chord_name = self.db.chords[chord_spelling]
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
    
class Quiz:
    def __init__(self):
        self.db = Database()
        self.key = None
        self.key_name = None

        # All questions
        self.ask_question = True
        self.correct_answer = None

        # Intervals
        self.interval_root = None
        self.interval_top = None
        self.interval_name = None
      
        # Chord names
        self.chord_spelling = None
        self.no_inversions = True
        self.sevenths = False

        # Chord positions
        self.chord_degree = None
        self.diatonic_7ths = False
        
    def get_interval_question(self):
        if self.key == 'All keys':
            self.root = random.choice(self.db.note_names)
        else:
            self.root = self.key

        random_interval = random.choice(range(1, 13))
        self.interval_name = self.db.interval_dict[random_interval]
        self.interval_top = self.db.intervals_by_key[self.root][random_interval]

        print(f"root: {self.root}")
        print(f"random_interval: {random_interval}")
        print(f"interval_name: {self.interval_name}")

        return [self.root, self.interval_top, self.interval_name]

    def get_chord_name_question(self):    
        if self.sevenths == False:
            pool = self.db.major_and_minor_chords
        else:
            pool = self.db.seventh_chords
        
        if self.no_inversions:
            pool_list = [(key, value) for key, value in pool.items() 
                                if '(' not in value]
        else:    
            pool_list = [(key, value) for key, value in pool.items()]     

        chord_name, self.answer = random.choice(pool_list)
        
        print(f"chord_name: {chord_name}")
        print(f"answer: {self.answer}")
        
        return chord_name, self.answer
    
    def get_chord_degree_question(self):    
        if self.key == 'All keys':
            self.key_name = f'{random.choice(self.db.note_names)} major'
            #print(key_name)
        else:
            self.key_name = f'{self.key} major'

        if self.diatonic_7ths:    
            pool = self.db.dia_7th[self.key_name]
        else:
            pool = self.db.dia_maj[self.key_name]
        
        pool_list = [[key, value] for key, value in pool.items()]
            
        self.chord_degree, self.correct_answer = random.choice(pool_list)
        return self.chord_degree, self.correct_answer
        

if __name__ == '__main__':
    db = Database()