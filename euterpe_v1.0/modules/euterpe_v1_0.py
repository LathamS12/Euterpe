import os
import random

import pygame
import pygame.midi 

from unittest.mock import MagicMock

from music_v1 import Piano, Database


BLACK = (0, 0, 0)
GRAY = (111, 111, 111)
WHITE = (255, 255, 255)
BLUE = (12, 148, 205)

parent_dir = os.path.dirname(os.getcwd())
ASSET_FOLDER = f'{parent_dir}/assets'

class Game:
    def __init__(self):
        self._setup()
        self.piano = Piano()
        self.db = Database()
        self.gui = GUI()
        self.midi_input = open_midi_stream()
        
        self.state = 'welcome_screen'
        #self.state = 'menu'
        #self.state = 'interval_quiz'
        #self.state = 'free_play'

        self.key = None
        self.quiz_active = False
        self.no_octaves = False

    def _setup(self):
        init_pygame()
    
    def run_game(self):
        running = True
        while running:
            if self.state == 'welcome_screen':
                self.welcome_screen()

            elif self.state == 'menu':
                self.menu()

            elif self.state == 'free_play':
                self.free_play()

            elif self.state == 'interval_quiz':
                self.interval_quiz()   

            elif self.state == 'chord_quiz':
                self.chord_quiz()  

    def welcome_screen(self):
        image = pygame.image.load(f'{ASSET_FOLDER}/welcome screen.png').convert()
        image_xy = self.gui.get_centered_xy(image)
        self.gui.draw_image_to_screen(image, image_xy)

        while True:
            self.event_handler()      
            if self.piano.get_pressed_k12() == ['C']:
                self.state = 'menu'
                break
    
    def menu(self):
        self.key = None

        image = pygame.image.load(f'{ASSET_FOLDER}/menu.png').convert()
        image_xy = self.gui.get_centered_xy(image)
        self.gui.draw_image_to_screen(image, image_xy)

        while True:
            self.event_handler()
            
            if self.piano.get_pressed_k12() == ['G']:
                self.state = 'free_play'
                break

            if self.piano.get_pressed_k12() == ['B']:
                self.state = 'interval_quiz'
                break

            if self.piano.get_pressed_k12() == ['D']:
                self.state = 'chord_quiz'
                break



    def free_play(self): 
        self.gui.reset_screen()
        #options = pygame.image.load(f'{ASSET_FOLDER}/options.png').convert()
        #self.gui.draw_image_to_screen(options, [50, 50])

        self.event_handler()

        pressed_keys = self.piano.get_pressed_key_vals()
        note_text = None
        text_size = 120

        if pressed_keys==[108]: #octave number toggle
            self.no_octaves = 0 if self.no_octaves==1 else 1
            pygame.time.delay(300)

        if len(pressed_keys) == 1:
            note = self.db.get_note_name(pressed_keys[0]) 
            text_size = 120      
            if self.no_octaves:
                note_text = self.db.get_note_name(pressed_keys[0])
            else:
                note_text = note[:-1]

        elif len(pressed_keys) == 2:
            if self.no_octaves:
                names = [self.db.get_note_name(x) for x in pressed_keys]
            else:
                names = [self.db.get_note_name(x)[:-1] for x in pressed_keys]

            interval = pressed_keys[1] - pressed_keys[0]
            interval_name = self.db.get_interval_names([interval])[0] 
            note_text = f'{names[0]} {names[1]}\n{interval_name}' 

        elif len(pressed_keys) >= 3:         
            chord = self.piano.get_pressed_chord()
            if chord == None:
                chord = ''
        
            if self.no_octaves:
                note_text = f"{' '.join(self.piano.get_pressed_key_names())}\n{chord}"
            else:
                k12_notes = [x[:-1] for x in self.piano.get_pressed_key_names()]
                notes = ' '.join(k12_notes)                        
                note_text = f"{notes}\n{chord}"
        
        if note_text:
            self.gui.draw_text_to_screen(note_text, text_size, BLUE, -25)
        else:
            self.gui.draw_text_to_screen('', text_size, BLUE, -25)        
    
    def interval_quiz(self):
        self.quiz_active = True
        self._select_key()
        input = []
        last_printed = [] 
        
        root, interval, answer = self.db.get_interval_question(self.key)
        
        if interval=='octave':
            text = f'Play an {interval}\nabove {root}'
        else:
            text = f'Play a {interval}\nabove {root}'

        self.gui.reset_screen() 
        self.gui.draw_text_to_screen(text, 100, BLUE, -60)
        self.gui.draw_text_to_screen(f'Key: {self.key}', 40, BLUE, 120)

        while self.quiz_active:             
            self.event_handler()
            input = self.piano.get_pressed_k12()
            compare = [root, answer]  
            if len(input)>0:
                if last_printed != input:
                    last_printed = input
                    print(f'input: {input}, compare: {compare}') 
    
            if input==[root, answer]:
                print('correct!')
                break # question loop

    def chord_quiz(self):
        self.quiz_active = True
        #self._select_key()
        chord_spelling, answer = self.db.get_chord_question(self.key)
        
        if answer.split()[0] in ['A', 'A#', 'F', 'F#', 'E', 'E#']:
            text = f'Play an {answer}'
        else:
            text = f'Play a {answer}'

        print(f'chord_spelling: {chord_spelling}')
        self.gui.reset_screen() 
        self.gui.draw_text_to_screen(text, 100, BLUE, -15)
        self.gui.draw_text_to_screen(f'Key: {self.key}', 40, BLUE, 120)

        while self.quiz_active:              
            self.event_handler()
            input = self.piano.get_pressed_k12()
            
            if ' '.join(input) == chord_spelling:
                print('correct!')
                break


    def _select_key(self):
        print(f'self.key: {self.key}')
        if self.key is not None:
            return
        else:
            pygame.time.delay(500) # So the previous input isn't used
            self.gui.reset_screen()
            text = f'Play a note C4-B4 to select a key.\nPlay any other note to select all keys'
            self.gui.draw_text_to_screen(text, 60, BLUE, -60)

            while True:        
                self.event_handler()
                input = self.piano.get_pressed_key_vals()
                
                response = None
                if len(input)==1:
                    response = input[0]
                    
                    if 59 < response < 72:
                        print(f'key of {self.db.get_note_k12(response)} selected')
                        self.key = self.db.get_note_k12(response)
                    else:               
                        self.key = 'All'
                    
                    break

    def event_handler(self):
        self._post_midi_as_pygame()            
        
        for e in pygame.event.get():
            if e.type in [pygame.midi.MIDIIN]:     
                if e.__dict__['status'] == 176: # Pedal
                    print('pedal')
                else: #Key presses
                    key_val = e.__dict__['data1']
                    if key_val !=0:
                        is_key_pressed = self.piano.key_status
                        is_key_pressed[key_val] = 0 if is_key_pressed[key_val] == 1 else 1
  
                if self.piano.get_pressed_key_names() == ['A0', 'B0']:  
                    self.state = 'menu'
                    self.quiz_active = False

                    return

            if (e.type in [pygame.QUIT]) or (e.type in [pygame.KEYDOWN]):
                self.quit_game() 

    def _post_midi_as_pygame(self): 
        if self.midi_input.poll(): 
            midi_events = self.midi_input.read(10)
            pygame_events = pygame.midi.midis2events(midi_events, 
                                                     self.midi_input.device_id)
            
            for pe in pygame_events:
                pygame.event.post(pe)         
            return pygame_events #Only returning these for testing

    def quit_game(self):
        close_midi_stream()
        pygame.quit()



class GUI:
    def __init__(self):
        self.screen = self._create_screen(800, 600)

    def _create_screen(self, width, height):
        screen = pygame.display.set_mode((width, height))
        return screen
    
    #Utility functions
    def reset_screen(self):
        self.screen.fill(BLACK)

    def draw_image_to_screen(self, image, top_left_corner):
        self.screen.blit(image, top_left_corner)
        self.update_screen()

    def draw_text_to_screen(self, text, size, color, offset):
        font = pygame.font.Font(None, size) #None for default font 
        lines = text.split('\n')
        y_offset = offset
        for line in lines:
            text_render = font.render(line, True, color)
            x, y = self.get_centered_xy(text_render)
            self.screen.blit(text_render, (x, y + y_offset))
            y_offset += 100
   
        self.update_screen()


    def update_screen(self):
        pygame.display.flip()

    #Graphics functions
    def get_centered_xy(self, surface):
        rect = surface.get_rect()
        centered_x = (self.screen.get_width() - rect.width) // 2
        centered_y = (self.screen.get_height() - rect.height) // 2
        return [centered_x, centered_y]

    def random_color(self):
        rcolor1 = round(random.random()*255)
        rcolor2 = round(random.random()*255)
        rcolor3 = round(random.random()*255)
        return (rcolor1, rcolor2, rcolor3)


#Streaming functions
def init_pygame():
    pygame.init()
    pygame.midi.init()

def open_midi_stream():
    input_id = pygame.midi.get_default_input_id()
    input = pygame.midi.Input(input_id)
    print("Digital piano ready")
    return input

def close_midi_stream():
    pygame.midi.quit()


def get_midi_type(event):
    return event.__dict__['']

if __name__ == '__main__':
    game = Game()
    game.run_game()