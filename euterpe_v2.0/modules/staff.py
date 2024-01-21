import sys
import pygame
import pygame_gui
import random

ASSET_FOLDER = f'C:/Users/Scott/Dropbox/Data_Science/Portfolio/euterpe_v2.0/assets'
dejavu_serif = f'{ASSET_FOLDER}/DejaVuSerif.ttf'
BLUE = (12, 148, 205)

class Staff:
    def __init__(self, width, height):

        self.width = width
        self.height = height

        # Define the staff properties
        self.line_spacing = self.height / 30
        self.lines = 11
        self.staff_left = (width // 10)
        self.staff_right = (width // 2.5)
        self.staff_length = self.staff_right - self.staff_left

        self.staff_top = height // 3
        self.staff_bottom = self.staff_top + (self.lines*self.line_spacing)

        self.treble_clef = pygame.image.load(f'{ASSET_FOLDER}/treble clef blue.png').convert_alpha()
        self.bass_clef = pygame.image.load(f'{ASSET_FOLDER}/bass clef blue.png').convert_alpha()
        self.pedal_image = pygame.image.load(f'{ASSET_FOLDER}/pedal.png').convert_alpha()

        self.staff_positions = {i: 0 for i in range(52)}

        # Define the note properties
        self.note_y_coords = self._build_y_coord_dict()
        
        self.note_height = self.line_spacing
        self.note_width = self.note_height*1.25
        
        #pygame.Color('white')
        self.note_color = BLUE
        self.ledger_line_color = BLUE
        self.ledger_line_length = self.note_width*1.3

    def _build_y_coord_dict(self):
        staff_notes = ['B', 'A', 'G', 'F', 'E', 'D', 'C']
        octaves = range(7, -1, -1)
        note_y_coords = {}
        y_lowest_note = self.height/30
        increment = self.line_spacing/2

        y = y_lowest_note
        for octave in octaves:
            for note in staff_notes:
                note_y_coords[f'{note}{str(octave)}'] = y
                y += increment

        return note_y_coords
    
    def render(self, screen, piano_status):
        pressed_keys, pedal = piano_status
        
        self.draw_music_staff(screen)

        notes = self.create_notes(pressed_keys)
        
        if notes:
            self.shift_overlapping_notes(notes)
            self.draw_notes(notes, screen)
            self.draw_ledger_lines(notes, screen)

        if pedal:
            screen.blit(self.pedal_image, (self.staff_left, self.staff_bottom))

    def draw_music_staff(self, screen):
        # Staff lines
        for i in range(self.lines):
            y = self.staff_top + i*self.line_spacing
            if i == 5:
                pygame.draw.line(screen, pygame.Color('black'), (self.staff_left, y), (self.staff_right, y))
            else:
                pygame.draw.line(screen, BLUE, (self.staff_left, y), (self.staff_right, y))

        # Clefs
        treble_height = (self.line_spacing*5)*1.2
        treble_width = treble_height*.4
        
        resized_treble = pygame.transform.scale(self.treble_clef, (treble_width, treble_height))
        screen.blit(resized_treble, (self.staff_left + 10, self.staff_top-(self.line_spacing/2)))

        bass_height = (self.line_spacing*5)*.7
        bass_width = bass_height*.8

        resized_bass = pygame.transform.scale(self.bass_clef, (bass_width, bass_height))
        screen.blit(resized_bass, (self.staff_left + 10, self.staff_bottom-(self.line_spacing*5)))
   
    def create_notes(self, pressed_keys):
        notes = []

        for i in range(len(pressed_keys)):     
            note = Note(pressed_keys[i])

            if note.name != 'C8':
                
                if '#' in note.name:
                    note.sharp = True

                if 'b' in note.name:
                    note.flat = True

                name_no_accidentals = note.name.replace('#', '').replace('b', '')
                
                note.x = self.staff_right - (self.staff_length/2.5) 
                note.y = self.note_y_coords[name_no_accidentals]

                notes.append(note)

            else:
                pass

        return notes

    def shift_overlapping_notes(self, notes):
        for i in range(len(notes)-1):
            if notes[i].y - notes[i+1].y <= self.note_height / 2:
                notes[i+1].x_offset = True
                notes[i+1].x += self.note_width*.85
                notes[i+1].acc_offset = -.85*self.note_width

            if notes[i].x_offset == True and notes[i+1].x_offset == True:
                notes[i+1].x_offset = False
                notes[i+1].x -= self.note_width*.85
                notes[i+1].acc_offset = 0


    def draw_notes(self, notes, screen):
        for note in notes: 
            note_rect = pygame.Rect(note.x, note.y, self.note_width, self.note_height)
            pygame.draw.ellipse(screen, self.note_color, note_rect)

            if note.sharp:
                font = pygame.font.Font(dejavu_serif, 40)
                text_render = font.render('♯', True, self.note_color)
                sharp_x = note.x-(self.note_width*.8) + note.acc_offset
                screen.blit(text_render, (sharp_x, note.y-12)) 

            if note.flat:
                font = pygame.font.Font(dejavu_serif, 48)
                text_render = font.render('♭', True, self.note_color)
                flat_x = note.x-(self.note_width*.8) + note.acc_offset
                screen.blit(text_render, (flat_x, note.y-22)) 
        
    def draw_ledger_lines(self, notes, screen):   
        for note in notes:
            ledger_left = note.x + (self.note_width/2) - (self.ledger_line_length/2)
            ledger_right = note.x + (self.note_width/2) + self.ledger_line_length/2

            # Middle C
            mid_point = (self.staff_top + self.staff_bottom)/2

            if note.y + (self.note_height) == mid_point:
                pygame.draw.line(screen, self.ledger_line_color, 
                                (ledger_left, mid_point-self.line_spacing/2), 
                                (ledger_right, mid_point-self.line_spacing/2))

            # Below staff
            if note.y + (self.note_height) >= self.staff_bottom:
                num_ledger_lines = int((note.y + (self.note_height*1.5) - self.staff_bottom) 
                                       // self.line_spacing)

                for i in range(num_ledger_lines):
                    ledger_line_y = self.staff_bottom + i*self.line_spacing
                    pygame.draw.line(screen, self.ledger_line_color, 
                                    (ledger_left, ledger_line_y), 
                                    (ledger_right, ledger_line_y))

            # Above staff
            elif (note.y + self.note_height*1.5) <= self.staff_top:
                num_ledger_lines = int((self.staff_top - (note.y-self.note_height/2))  
                                           // self.line_spacing)
                
                for i in range(num_ledger_lines):
                    ledger_line_y = self.staff_top - i*self.line_spacing

                    pygame.draw.line(screen, self.ledger_line_color, 
                                    (ledger_left, ledger_line_y), 
                                    (ledger_right, ledger_line_y))


class Note:
    def __init__(self, name):
        self.name = name
        self.x = None
        self.x_offset = False
        self.y = None
        self.sharp = False
        self.flat = False
        self.acc_offset = 0


def random_color():
    rcolor1 = random.randint(50, 255)
    rcolor2 = random.randint(50, 255)
    rcolor3 = random.randint(50, 255)
    return (rcolor1, rcolor2, rcolor3)
