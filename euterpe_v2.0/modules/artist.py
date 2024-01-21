import random
import pygame

BLUE = (12, 148, 205)
BLACK = (0, 0, 0)

class Artist:
    def __init__(self, width, height):
        self.running = False
        self.width = width
        self.height = height
        self.shapes = []
                    
        self.octave_colors = {  0: pygame.Color('red'), 
                                1: pygame.Color('orange'), 
                                2: pygame.Color('yellow'), 
                                3: pygame.Color('green'), 
                                4: pygame.Color('aqua'), 
                                5: pygame.Color('blue'), 
                                6: pygame.Color('purple'), 
                                7: pygame.Color('white'),
                                8: pygame.Color('black') }
                            
    def render(self, screen, pk_names):
        if self.running == False:
            screen.fill(BLACK)
            self.shapes = []
            self.running = True

        for note in pk_names:
            if random.random() < .60:
                pass
            else:
                if note == 'C8':
                    screen.fill(BLACK)
                    self.shapes = []

                key = note[:-1]
                octave = int(note[-1])
                color = self.octave_colors[octave] 

                if key == 'A':
                    self.shapes.append(RandRect(color))

                elif key == 'B':
                    self.shapes.append(RandCircle(color))
                
                elif key == 'C':
                    self.shapes.append(RandLine(color))  
                    
                elif key == 'D':
                    self.shapes.append(RandPoly(color, 3)) 
                
                elif key == 'E':
                    self.shapes.append(RandPoly(color, 5))

                elif key == 'F':
                    self.shapes.append(RandPoly(color, 8))
                    
                elif key == 'G':
                    self.shapes.append(RandArc(color))

                # Manipulate
                
                elif key == 'F#' or key == 'Bb':
                    self.move_shapes1(screen)
                
                elif key == 'C#' or key == 'Eb':
                    self.move_shapes2(screen)

                elif key == "G#" or key == 'Ab':
                    self.grow_shapes(screen)

                elif key == 'D#' or key == 'Db':
                    self.shrink_shapes(screen)
               
                elif key == 'A#' or key == 'Gb':
                    self.randomize_colors()
            
            self._draw_shapes(screen)
        
    def _draw_shapes(self, screen):               
        for shape in self.shapes:
            shape.draw(screen)
    
    def randomize_colors(self):
        for shape in self.shapes:
            shape.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    def move_shapes1(self, screen):
        screen.fill(BLACK)
        for shape in self.shapes:
            shape.move(shape.vector1)

    def move_shapes2(self, screen):
        screen.fill(BLACK)
        for shape in self.shapes:
            shape.move(shape.vector2)

    def grow_shapes(self, screen):
        screen.fill(BLACK)
        for shape in self.shapes:
            shape.grow()

    def shrink_shapes(self, screen):
        screen.fill(BLACK)
        for shape in self.shapes:
            shape.shrink()

    def vibrate_shapes(self):
        pass

class RandomShape:
    def __init__(self, color):
        self.color = color
        self.x_max = 1000
        self.y_max = 750

        self.vector1 = (random.randint(-10, 10), random.randint(-10, 10))
        self.vector2 = (random.randint(-15, 15), random.randint(-15, 15))
        self.growby1 = random.randint(0, 10)
        self.growby2 = random.randint(0, 10)
        self.shrinkby1 = random.randint(0, 10)
        self.shrinkby2 = random.randint(0, 10)


class RandRect(RandomShape):
    def __init__(self, color):
        super().__init__(color)
        
        self.x = random.randint(0, self.x_max)
        self.y = random.randint(0, self.y_max)
        self.width = random.randint(0, 100)
        self.height = random.randint(0, 100)    

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                         (self.x, self.y, self.width, self.height))
        
    def move(self, vector):
        self.x += vector[0]
        self.y += vector[1]
    
    def grow(self):
        self.width += self.growby1
        self.height += self.growby2
    
    def shrink(self):
        self.width -= self.shrinkby1
        self.height -= self.shrinkby2


class RandCircle(RandomShape):
    def __init__(self, color):
        super().__init__(color)

        self.x = random.randint(0, self.x_max)
        self.y = random.randint(0, self.y_max)
        self.radius = random.randint(0, 60)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self, vector):
        self.x += vector[0]
        self.y += vector[1]
    
    def grow(self):
        self.radius += self.growby1
    
    def shrink(self):
        self.radius -= self.shrinkby1


class RandLine(RandomShape):
    def __init__(self, color):
        super().__init__(color)
        max_dist = 400

        self.x1 = random.randint(0, self.x_max)
        self.y1 = random.randint(0, self.y_max)

        self.x2 = random.randint(self.x1, self.x1+max_dist)
        self.y2 = random.randint(self.y1, self.y1+max_dist)

        self.width = random.randint(0, 15)

    def draw(self, screen):
        pygame.draw.line(screen, self.color, 
                         (self.x1, self.y1), (self.x2, self.y2), self.width)

    def move(self, vector):
        self.x1 += vector[0]
        self.y1 += vector[1]
    
    def grow(self):
        if random.random() < 0.5:
            self.x2 += self.growby1
        else:
            self.y2 += self.growby2

    def shrink(self):
        if random.random() < 0.5:
            self.x2 -= self.shrinkby1
        else:
            self.y2 -= self.shrinkby2


class RandPoly(RandomShape):
    def __init__(self, color, sides):
        super().__init__(color)
        self.vertices = []
        max_dist = 100   

        x1 = random.randint(0, self.x_max)
        y1 = random.randint(0, self.y_max)
        self.vertices.append((x1, y1))

        for x in range(sides-1):
            x = random.randint(x1-max_dist, x1+max_dist)
            y = random.randint(y1-max_dist, y1+max_dist)
            self.vertices.append((x, y))

        self.width = random.randint(0, 7)

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.vertices, self.width)

    def move(self, vector):
        updated_xy = []
        for vert in self.vertices:
            x  = vert[0] + vector[0]
            y =  vert[1] + vector[1]
            updated_xy.append((x, y))
        self.vertices = updated_xy


    def grow(self):
        updated_xy = []
        for vert in self.vertices:
            if vert in self.vertices[0:2]:
                x = vert[0] + self.growby1
                y = vert[1] + self.growby1
            else:
                x = vert[0] - self.growby2
                y = vert[1] - self.growby2
            updated_xy.append((x, y))
        self.vertices = updated_xy

    def shrink(self):
        updated_xy = []
        for vert in self.vertices:
            if vert in self.vertices[0:2]:
                x = vert[0] - self.shrinkby1
                y = vert[1] - self.shrinkby1
            else:
                x = vert[0] + self.shrinkby2
                y = vert[1] + self.shrinkby2
            updated_xy.append((x, y))
        self.vertices = updated_xy


class RandArc(RandomShape):  
    def __init__(self, color):
        super().__init__(color)
        
        x = random.randint(0, self.x_max)
        y = random.randint(0, self.y_max)
        width = random.randint(0, 100)
        height = random.randint(0, 100)
        self.arc_rect = [x, y, width, height]

        self.begin = random.randint(0, 360)
        self.end = random.randint(self.begin, 360)
        self.width = random.randint(0, 15)
 
    def draw(self, screen):
        pygame.draw.arc(screen, self.color, self.arc_rect, 
                        self.begin, self.end, self.width)
    def move(self, vector):
        self.arc_rect[0] += vector[0]
        self.arc_rect[1] += vector[1]

    def grow(self):
        self.arc_rect[2] += self.growby1
        self.arc_rect[3] += self.growby2

    def shrink(self):
        self.arc_rect[2] -= self.shrinkby1
        self.arc_rect[3] -= self.shrinkby2


