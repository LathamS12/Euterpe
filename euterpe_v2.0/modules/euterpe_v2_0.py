import os
import random
import pygame
import pygame.midi
import textwrap
import pygame_gui

from music import Piano, Database, Quiz
from staff import Staff
from artist import Artist

ASSET_FOLDER = f'C:/Users/Scott/Dropbox/Data_Science/Portfolio/euterpe_v2.0/assets'
SOUNDS = f'{ASSET_FOLDER}/sounds'
dejavu_serif = f'{ASSET_FOLDER}/DejaVuSerif.ttf'

BLACK = (0, 0, 0)
GRAY = (111, 111, 111)
WHITE = (255, 255, 255)
BLUE = (12, 148, 205)

class Game:
    def __init__(self, screen_width, screen_height):   
        self.width = screen_width
        self.height = screen_height

        self.piano = Piano()
        self.db = Database('sharp')
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Euterpe')

        self.staff = Staff(self.width, self.height)
        self.artist = Artist(self.width, self.height)

        self.input_id = pygame.midi.get_default_input_id()
        self.midi_input = pygame.midi.Input(self.input_id)

        self.state = 'welcome_screen'
        #self.state = 'menu'
        #self.state = 'interval_quiz'
        #self.state = 'chord_name_quiz'
        #self.state = 'chord_degree_quiz'
        #self.state = 'free_play'
        #self.state = 'art_mode'

        self.is_running = True
        self.no_octaves = True
        self.mode = 'sharp'
        self.quiz = Quiz()

        self.bell = pygame.mixer.Sound(f'{SOUNDS}/bell.wav')

    def interpret_midi(self, midi_input): 
        if self.midi_input.poll(): 
            midi_events = self.midi_input.read(10)
            pygame_events = pygame.midi.midis2events(midi_events, 
                                                        midi_input.device_id)
            
            for pe in pygame_events:
                pygame.event.post(pe)         
            return pygame_events # For testing

    def welcome_screen(self):
        image = pygame.image.load(f'{ASSET_FOLDER}/welcome screen.png').convert() 
        image_xy = self.get_centered_xy(image) 
        self.screen.blit(image, image_xy)
    
        if self.piano.get_pressed_k12() == ['C']:
            self.state = 'menu'
    

    def menu(self): 
        if self.mode == 'sharp':
            menu_image = pygame.image.load(f'{ASSET_FOLDER}/menu sharp.png').convert() 
            menu_image_xy = self.get_centered_xy(menu_image) 

        elif self.mode == 'flat':
            menu_image = pygame.image.load(f'{ASSET_FOLDER}/menu flat.png').convert() 
            menu_image_xy = self.get_centered_xy(menu_image) 
        
        self.screen.blit(menu_image, menu_image_xy)

        #Select menu options
        pressed_keys = self.piano.get_pressed_k12()
        if pressed_keys == ['A']:
            self.toggle_sharp_flat()
            pygame.time.delay(300)

        if pressed_keys == ['E']:
            self.state = 'free_play'
            pygame.time.delay(300)
            
        if pressed_keys == ['G']:
            self.state = 'interval_quiz'
            pygame.time.delay(300)
            
        if pressed_keys == ['B']:
            self.state = 'chord_name_quiz'
            pygame.time.delay(300)

        if pressed_keys == ['D']:
            self.state = 'chord_degree_quiz'
            pygame.time.delay(300)

        if pressed_keys == ['F']:
            self.state = 'art_mode'
            pygame.time.delay(300)    

    def toggle_sharp_flat(self):
        if self.mode == 'sharp':
            self.mode = 'flat'
            self.db = Database('flat')
            self.piano.db = Database('flat')
            self.quiz.db = Database('flat')

        elif self.mode == 'flat':
            self.mode = 'sharp'
            self.db = Database('sharp')
            self.piano.db = Database('sharp')
            self.quiz.db = Database('sharp')

    def free_play(self): 
        self.screen.fill(BLACK)
        piano_status = self.piano.get_piano_status()
        self.staff.render(self.screen, piano_status)

        pressed_keys = self.piano.get_pressed_key_vals()
        note_text = None
        chord_text = None

        if pressed_keys==[108]: #octave number toggle
            self.no_octaves = toggle(self.no_octaves)
            pygame.time.delay(300)

        if len(pressed_keys) == 1:
            note = self.db.get_note_name(pressed_keys[0])      
            if self.no_octaves:
                note_text = note[:-1]  
            else:
                note_text = self.db.get_note_name(pressed_keys[0])  

        elif len(pressed_keys) == 2:
            if self.no_octaves:
                names = [self.db.get_note_name(x)[:-1] for x in pressed_keys]       
            else:
                names = [self.db.get_note_name(x) for x in pressed_keys]

            interval = pressed_keys[1] - pressed_keys[0]
            interval_name = self.db.get_interval_names([interval])[0] 
            note_text = f'{names[0]} {names[1]}'
            chord_text = f'{interval_name}' 

        elif len(pressed_keys) >= 3:         
            chord = self.piano.get_pressed_chord()
            if chord == None:
                chord = ''
        
            if self.no_octaves:
                k12_notes = [x[:-1] for x in self.piano.get_pressed_key_names()]
                notes = ' '.join(k12_notes)                        
                note_text = f'{notes}'
                chord_text = f'{chord}'
            else:
                note_text = f"{' '.join(self.piano.get_pressed_key_names())}"
                chord_text = f'{chord}'
               
        
        if note_text:
            self.draw_text_multi_line(note_text, -50, 200, 20)     
            
            if chord_text:
                self.draw_text_multi_line(chord_text, 50, 200, 25)

        else:
            self.draw_text_to_screen('', -100, 0, 50, BLUE)        

    def art_mode(self): 
        pk_names = self.piano.get_pressed_key_names() 
        self.artist.render(self.screen, pk_names)
            

    def interval_quiz(self):
        q = self.quiz

        if q.key is None:    
            q.key = self._select_key()
            print('Selected key:', q.key)   

        else:    
            input = []
            last_printed = [] 

            if q.ask_question:
                q.interval_root, q.interval_top, q.interval_name = q.get_interval_question()
                q.ask_question = False

            else:
                input = self.piano.get_pressed_k12()
                q.correct_answer = [q.interval_root, q.interval_top]  

                if len(input) > 0:
                    if last_printed != input:
                        last_printed = input
                        print(f'input: {input}, correct: {q.correct_answer}') 

                q.check_answer(input, q.correct_answer)


    def interval_quiz_draw(self):
        if self.quiz.key == None:
            self.screen.fill(BLACK)
            text = f'Play a note C4-B4 to select a root note.\nPlay any other note to select all roots'
            self.draw_text_to_screen(text, -60, 0, 60, BLUE)

        else:
            if self.quiz.interval_name=='octave':
                text = f'Play an {self.quiz.interval_name}\nabove {self.quiz.interval_root}'
            else:
                text = f'Play a {self.quiz.interval_name}\nabove {self.quiz.interval_root}'
        
            self.screen.fill(BLACK) 
            self.draw_text_to_screen(text, -60, 0, 100, BLUE)


    def chord_name_quiz(self):
        q = self.quiz
        pressed_keys = self.piano.get_pressed_key_vals()
        
        if pressed_keys==[108]:
            q.sevenths = toggle(q.sevenths)
            q.ask_question = True
            pygame.time.delay(300)

        if pressed_keys==[107]:
            q.names_no_inversions = toggle(q.names_no_inversions)
            q.ask_question = True
            pygame.time.delay(300)
            
        if q.ask_question:
            q.correct_answer, q.chord_name = q.get_chord_name_question()
            q.ask_question = False

        else:   
            input = self.piano.get_pressed_k12() 
            print('input:', input)
            print('correct:', q.correct_answer)

            q.check_answer(input, q.correct_answer)

    def chord_name_quiz_draw(self):
        if self.quiz.chord_name[0] in ['A', 'A#', 'F', 'F#', 'E', 'E#']:
            text = f'Play an {self.quiz.chord_name}'
        else:
            text = f'Play a {self.quiz.chord_name}'
  
        self.screen.fill(BLACK)
        self.draw_text_to_screen(text, -50, 0, 100, BLUE)


    def chord_degree_quiz(self):
        q = self.quiz
        pressed_keys = self.piano.get_pressed_key_vals()

        if pressed_keys==[108]:
            q.diatonic_7ths = toggle(q.diatonic_7ths)
            q.ask_question = True
            pygame.time.delay(300)

        if q.key is None:    
            q.key = self._select_key()
 
        else:
            if q.ask_question:
                q.chord_degree, q.correct_answer = q.get_chord_degree_question()
                q.ask_question = False
            else:   
                input = self.piano.get_pressed_k12()

                q.check_answer(input, q.correct_answer)

  
    def chord_degree_quiz_draw(self):
        self.screen.fill(BLACK)

        if self.quiz.key == None:
            self.screen.fill(BLACK)
            text = f'Play a note C4-B4 to select a key.\nPlay any other note to select all keys'
            self.draw_text_to_screen(text, -60, 0, 60, BLUE)

        else:
            self.screen.fill(BLACK)

            if self.quiz.diatonic_7ths:
                text = f'Play the {self.quiz.chord_degree} 7 chord'
                self.draw_text_to_screen(text, -60, 0, 80, BLUE)

            else:
                text = f'Play the {self.quiz.chord_degree} chord'
                self.draw_text_to_screen(text, -60, 0, 80, BLUE)

            self.draw_text_to_screen(f'Key: {self.quiz.key_name}', 20, 0, 40, BLUE)

    def _select_key(self):             
        input = self.piano.get_pressed_key_vals()
        
        response = None
        if len(input)==1:
            response = input[0]
            
            if 59 < response < 72:
                print(f'key of {self.db.get_note_k12(response)} selected')
                return self.db.get_note_k12(response)
            else:               
                return 'All keys'


    def draw_text_to_screen(self, text, y_offset, x_offset, size, color):
        font = pygame.font.Font(None, size) #None for default font 
        lines = text.split('\n')

        for line in lines:
            text_render = font.render(line, True, color)
            x, y = self.get_centered_xy(text_render)
            self.screen.blit(text_render, (x + x_offset, y + y_offset))
            y_offset += 100



    def draw_text_multi_line(self, text, y_offset, x_offset, twidth, size=80, color=BLUE):
        font = pygame.font.Font(None, size) #None for default font 
        lines = textwrap.wrap(text, width=twidth)
        
        for line in lines:
            text_render = font.render(line, True, color)
            x, y = self.get_centered_xy(text_render)
            self.screen.blit(text_render, (x + x_offset, y + y_offset))
            y_offset -= 100


    def draw_heads_up(self):
        if self.state == 'welcome_screen' or self.state == 'menu':
            pass
        else:
            image = pygame.image.load(f'{ASSET_FOLDER}/return to menu.png').convert()
            self.screen.blit(image, (1, 620))

        if self.state == 'free_play':
            image = pygame.image.load(f'{ASSET_FOLDER}/toggle octaves.png').convert()
            self.screen.blit(image, (700, 610))

        if self.state == 'chord_name_quiz' or self.state =='chord_degree_quiz':
            image = pygame.image.load(f'{ASSET_FOLDER}/toggle 7ths.png').convert()
            self.screen.blit(image, (700, 620))

        if self.state == 'chord_name_quiz':
            image = pygame.image.load(f'{ASSET_FOLDER}/toggle inversions.png').convert()
            self.screen.blit(image, (350, 620))

        if self.state == 'art_mode':
            image = pygame.image.load(f'{ASSET_FOLDER}/clear screen.png').convert()
            self.screen.blit(image, (700, 630))


    def get_centered_xy(self, surface):
        rect = surface.get_rect()
        centered_x = (self.screen.get_width() - rect.width) // 2
        centered_y = (self.screen.get_height() - rect.height) // 2
        return [centered_x, centered_y]


# Methods not in any class 
def toggle(value):
    return 0 if value == 1 else 1

def random_color():
    rcolor1 = random.randint(0, 255)
    rcolor2 = random.randint(0, 255)
    rcolor3 = random.randint(0, 255)
    return (rcolor1, rcolor2, rcolor3)

def get_midi_type(event):
    return event.__dict__['']


if __name__ == '__main__':
    pass