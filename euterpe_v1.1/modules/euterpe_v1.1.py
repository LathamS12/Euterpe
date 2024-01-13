import os
import random
import pygame
import pygame.midi
import pygame_gui

from music import Piano, Database, Quiz

ASSET_FOLDER = f'C:/Users/Scott/Dropbox/Data_Science/Portfolio/euterpe_v1.1/assets'

BLACK = (0, 0, 0)
GRAY = (111, 111, 111)
WHITE = (255, 255, 255)
BLUE = (12, 148, 205)

class Game:
    def __init__(self):   
        self.piano = Piano()
        self.db = Database()
        self.screen = pygame.display.set_mode((1000, 750))
        pygame.display.set_caption('Euterpe')

        self.input_id = pygame.midi.get_default_input_id()
        self.midi_input = pygame.midi.Input(self.input_id)

        self.state = 'welcome_screen'
        #self.state = 'menu'
        #self.state = 'interval_quiz'
        #self.state = 'chord_name_quiz'
        #self.state = 'chord_degree_quiz'
        #self.state = 'free_play'
        
        self.is_running = True
        self.no_octaves = True
        self.quiz = Quiz()


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
        menu_image = pygame.image.load(f'{ASSET_FOLDER}/menu.png').convert() 
        menu_image_xy = self.get_centered_xy(menu_image) 
        self.screen.blit(menu_image, menu_image_xy)

        pressed_keys = self.piano.get_pressed_k12()
        if pressed_keys == ['G']:
            self.state = 'free_play'
            pygame.time.delay(300)
            
        if pressed_keys == ['B']:
            self.state = 'interval_quiz'
            pygame.time.delay(300)
            
        if pressed_keys == ['D']:
            self.state = 'chord_name_quiz'
            pygame.time.delay(300)

        if pressed_keys == ['F']:
            self.state = 'chord_degree_quiz'
            pygame.time.delay(300)
            
    def free_play(self): 
        self.screen.fill(BLACK)
        #options = pygame.image.load(f'{ASSET_FOLDER}/options.png').convert()
        #self.gui.draw_image_to_screen(options, [50, 50])
        pressed_keys = self.piano.get_pressed_key_vals()
        note_text = None
        text_size = 120

        if pressed_keys==[108]: #octave number toggle
            self.no_octaves = toggle(self.no_octaves)
            pygame.time.delay(300)

        if len(pressed_keys) == 1:
            note = self.db.get_note_name(pressed_keys[0]) 
            text_size = 120      
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
            note_text = f'{names[0]} {names[1]}\n{interval_name}' 

        elif len(pressed_keys) >= 3:         
            chord = self.piano.get_pressed_chord()
            if chord == None:
                chord = ''
        
            if self.no_octaves:
                k12_notes = [x[:-1] for x in self.piano.get_pressed_key_names()]
                notes = ' '.join(k12_notes)                        
                note_text = f"{notes}\n{chord}"
            else:
                note_text = f"{' '.join(self.piano.get_pressed_key_names())}\n{chord}"
               
        
        if note_text:
            self.draw_text_to_screen(note_text, text_size, BLUE, -100)
        else:
            self.draw_text_to_screen('', text_size, BLUE, -100)        


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

            input = self.piano.get_pressed_k12()
            q.correct_answer = [q.interval_root, q.interval_top]  

            if len(input) > 0:
                if last_printed != input:
                    last_printed = input
                    print(f'input: {input}, correct: {q.correct_answer}') 

            if input==q.correct_answer:
                q.ask_question = True
                print('correct!')

    def interval_quiz_draw(self):
        if self.quiz.key == None:
            self.screen.fill(BLACK)
            text = f'Play a note C4-B4 to select a root note.\nPlay any other note to select all roots'
            self.draw_text_to_screen(text, 60, BLUE, -60)

        else:
            if self.quiz.interval_name=='octave':
                text = f'Play an {self.quiz.interval_name}\nabove {self.quiz.interval_root}'
            else:
                text = f'Play a {self.quiz.interval_name}\nabove {self.quiz.interval_root}'
        
            self.screen.fill(BLACK) 
            self.draw_text_to_screen(text, 100, BLUE, -60)


    def chord_name_quiz(self):
        q = self.quiz
        pressed_keys = self.piano.get_pressed_key_vals()
        
        if pressed_keys==[108]:
            q.sevenths = toggle(q.sevenths)
            q.ask_question = True
            pygame.time.delay(300)

        if pressed_keys==[107]:
            q.no_inversions = toggle(q.no_inversions)
            q.ask_question = True
            pygame.time.delay(300)
            
        if q.ask_question:
            q.chord_spelling, q.correct_answer = q.get_chord_name_question()
            q.ask_question = False

        else:   
            input = self.piano.get_pressed_k12()
            print(f'chord_spelling: {self.quiz.chord_spelling}') 

            if ' '.join(input) == q.chord_spelling:
                print('correct!')
                q.ask_question = True

    def chord_name_quiz_draw(self):
        if self.quiz.correct_answer.split()[0] in ['A', 'A#', 'F', 'F#', 'E', 'E#']:
            text = f'Play an {self.quiz.correct_answer}'
        else:
            text = f'Play a {self.quiz.correct_answer}'
  
        self.screen.fill(BLACK)
        self.draw_text_to_screen(text, 100, BLUE, -50)


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
            print(q.key)
            if q.ask_question:
                q.chord_degree, q.correct_answer = q.get_chord_degree_question()
                q.ask_question = False
            else:   
                input = self.piano.get_pressed_k12()
                print(f'chord_position: {q.chord_degree}, answer: {q.correct_answer}') 

                if input == q.correct_answer:
                    print('correct!')
                    q.ask_question = True

  
    def chord_degree_quiz_draw(self):
        self.screen.fill(BLACK)

        if self.quiz.key == None:
            self.screen.fill(BLACK)
            text = f'Play a note C4-B4 to select a key.\nPlay any other note to select all keys'
            self.draw_text_to_screen(text, 60, BLUE, -60)

        else:
            self.screen.fill(BLACK)

            if self.quiz.diatonic_7ths:
                text = f'Play the {self.quiz.chord_degree} 7 chord'
                self.draw_text_to_screen(text, 80, BLUE, -60)

            else:
                text = f'Play the {self.quiz.chord_degree} chord'
                self.draw_text_to_screen(text, 80, BLUE, -60)

            self.draw_text_to_screen(f'Key: {self.quiz.key_name}', 40, BLUE, 20)

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


    def draw_text_to_screen(self, text, size, color, offset):
        font = pygame.font.Font(None, size) #None for default font 
        lines = text.split('\n')
        y_offset = offset
        for line in lines:
            text_render = font.render(line, True, color)
            x, y = self.get_centered_xy(text_render)
            self.screen.blit(text_render, (x, y + y_offset))
            y_offset += 100


    def draw_heads_up(self):
        if self.state == 'welcome_screen' or self.state == 'menu':
            pass
        else:
            image = pygame.image.load(f'{ASSET_FOLDER}/return to menu.png').convert()
            self.screen.blit(image, (10, 600))

        if self.state == 'free_play':
            image = pygame.image.load(f'{ASSET_FOLDER}/toggle octaves.png').convert()
            self.screen.blit(image, (685, 590))

        if self.state == 'chord_name_quiz' or self.state =='chord_degree_quiz':
            image = pygame.image.load(f'{ASSET_FOLDER}/toggle 7ths.png').convert()
            self.screen.blit(image, (685, 600))

        if self.state == 'chord_name_quiz':
            image = pygame.image.load(f'{ASSET_FOLDER}/toggle inversions.png').convert()
            self.screen.blit(image, (350, 600))



    def get_centered_xy(self, surface):
        rect = surface.get_rect()
        centered_x = (self.screen.get_width() - rect.width) // 2
        centered_y = (self.screen.get_height() - rect.height) // 2
        return [centered_x, centered_y]


# Methods not in any class 
def toggle(value):
    return 0 if value == 1 else 1


 
# Game loop
pygame.init()
pygame.midi.init()

manager = pygame_gui.UIManager((800, 600))
clock = pygame.time.Clock()

game = Game()

while game.is_running:
    time_delta = clock.tick(60)/1000.0
    
    game.interpret_midi(game.midi_input)

    for event in pygame.event.get():
        if event.type in [pygame.QUIT, pygame.KEYDOWN]:
            game.is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            pass

        if event.type == pygame.midi.MIDIIN:     
            #print(event)
            
            if event.__dict__['status'] == 176: # Pedal
                print('pedal')
            else: #Key presses
                key_val = event.__dict__['data1']
                if key_val !=0:
                    is_key_pressed = game.piano.key_status
                    is_key_pressed[key_val] = 0 if is_key_pressed[key_val] == 1 else 1
                

        manager.process_events(event)

    manager.update(time_delta)
    
    if game.piano.get_pressed_key_names() == ['A0', 'B0']:
        game.state = 'menu'
        pygame.time.delay(300)

    if game.state == 'welcome_screen':
        game.welcome_screen()

    elif game.state == 'menu':
        game.quiz.ask_question = True
        game.quiz.key = None
        game.menu()

    elif game.state =='free_play':
        game.free_play()

    elif game.state == 'interval_quiz':
        game.interval_quiz()
        game.interval_quiz_draw()

    elif game.state == 'chord_name_quiz':
        game.chord_name_quiz()
        game.chord_name_quiz_draw()

    elif game.state == 'chord_degree_quiz':
        game.chord_degree_quiz()
        game.chord_degree_quiz_draw()

    else:
        #Default state
        game.screen.fill(BLACK)

    game.draw_heads_up()    
    manager.draw_ui(game.screen)
    pygame.display.update()

pygame.midi.quit()
pygame.quit()


#Graphics functions
def random_color(self):
    rcolor1 = random.randint(0, 255)
    rcolor2 = random.randint(0, 255)
    rcolor3 = random.randint(0, 255)
    return (rcolor1, rcolor2, rcolor3)


#Streaming functions
def get_midi_type(event):
    return event.__dict__['']

if __name__ == '__main__':
    pass