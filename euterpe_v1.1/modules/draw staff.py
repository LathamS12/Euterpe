import pygame
import pygame_gui

from piano_quiz_v1 import Game


# Initialize Pygame
pygame.init()

def staff_mode():
note_dictionary = {'C3':360, 'D3':350, 'E3':340, 'F3':330, 'G3':320, 'A3':310, 'B3':300, 
                        'C4':290, 'D4':280, 'E4':270, 'F4':260, 'G4':250, 'A4':240, 'B4':230, 
                       'C5':220, 'D5':210, 'E5':200, 'F5':190, 'G5':180, 'A5':170, 'B5':160, 
                       'C6':150, 'D6':140, 'E6':130, 'F6':120, 'G6':110, 'A6':100, 'B6':90, 
                       'C7':80, 'D7':70, 'E7':60, 'F7':50, 'G7':40, 'A7':30, 'B7':20, 
                       'C8':10
                       }


# Set the window size
window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Musical Staff")


def draw_text_to_screen(text, size, color, offset):
    font = pygame.font.Font(None, size) #None for default font 
    lines = text.split('\n')
    y_offset = offset
    for line in lines:
        text_render = font.render(line, True, color)
        x, y = get_centered_xy(text_render)
        window.blit(text_render, (x, y + y_offset))
        y_offset += 100

    pygame.display.flip()

def get_centered_xy(surface):
    rect = surface.get_rect()
    centered_x = (window_width - window_height) // 2
    centered_y = (window_width - window_height) // 2
    return [centered_x, centered_y]


# Create a Pygame GUI manager
manager = pygame_gui.UIManager((window_width, window_height))

# Define the staff properties
staff_spacing = 20
staff_lines = 11
staff_start_x = (window_width // 2) - 60
staff_start_y = window_height // 3


# Define the note properties
note_width = 25
note_height = 20
note_color = pygame.Color('white')
ledger_line_color = pygame.Color('white')
ledger_line_length = 15


# Run the main game loop
clock = pygame.time.Clock()
is_running = True
while is_running:
    time_delta = clock.tick(60) / 1000.0

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        manager.process_events(event)

    # Clear the window
    window.fill(pygame.Color('black'))

    # Draw the staff lines
    for i in range(staff_lines):
        y = staff_start_y + i*staff_spacing
        if i == 5:
            pygame.draw.line(window, pygame.Color('black'), (staff_start_x, y), (window_width - staff_start_x, y))
        else:
            pygame.draw.line(window, pygame.Color('white'), (staff_start_x, y), (window_width - staff_start_x, y))

    sharp_offset = 15
    notes = ['A#4', 'C6', 'B#3']
    for i, x in enumerate(notes):
        sharp = False
        if '#' in x: 
            sharp = True
            
        clean = notes[i].replace('#', '')
    
       
        # Draw a note
        note_x = staff_start_x + (2*staff_spacing) - note_width // 2
        sharp_x = note_x + 15 
    
        #if sharp:
            #pass
            #draw_text_to_screen('#', 50, pygame.Color('white'), sharp_x)
    
        note_y = note_dictionary[clean]
        note_rect = pygame.Rect(note_x, note_y, note_width, note_height)
        pygame.draw.ellipse(window, note_color, pygame.Rect(note_x, note_y, note_width, note_height))

        # Draw the ledger lines
        if note_y < staff_start_y:
            num_ledger_lines = abs((note_y - staff_start_y) // staff_spacing)
            for i in range(num_ledger_lines):
                ledger_line_y = staff_start_y - i*staff_spacing
                pygame.draw.line(window, ledger_line_color, (note_rect.left - ledger_line_length+40, ledger_line_y),
                                (note_rect.left, ledger_line_y))

        elif note_y + note_height > staff_start_y + staff_spacing*staff_lines:
            num_ledger_lines = abs((note_y + note_height - staff_start_y - staff_spacing * staff_lines) // staff_spacing)
            for i in range(num_ledger_lines):
                ledger_line_y = staff_start_y + (staff_lines*staff_spacing) + i*staff_spacing
                pygame.draw.line(window, ledger_line_color, (note_rect.left - ledger_line_length + 40, ledger_line_y),
                                (note_rect.left, ledger_line_y))
        

    # Update the GUI manager
    manager.update(time_delta)

    # Draw the GUI manager's UI
    manager.draw_ui(window)

    # Refresh the display
    pygame.display.update()

# Quit Pygame
pygame.quit()


 #200 is G5