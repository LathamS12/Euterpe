import pygame
import pygame.midi
import pygame_gui

import euterpe_v2_0 as et
 
# Game loop
pygame.init()
pygame.midi.init()


screen_width = 1000
screen_height = 750
manager = pygame_gui.UIManager((screen_width, screen_height))
clock = pygame.time.Clock()

game = et.Game(screen_width, screen_height)

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
                game.piano.pedal = True if game.piano.pedal == False else False
                
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
        game.artist.running = False
        game.menu()

    elif game.state =='free_play':
        game.free_play()

    elif game.state =='art_mode':
        game.art_mode()

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
        pass
    
    game.draw_heads_up()    
    manager.draw_ui(game.screen)
    pygame.display.update()

pygame.midi.quit()
pygame.quit()



if __name__ == '__main__':
    pass