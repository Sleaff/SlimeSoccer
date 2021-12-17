import pygame, sys, math

""" initital values etc """
pygame.init()
pygame.display.set_caption("Slime Soccer")
WIDTH, HEIGHT = 1600, 900
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
LIGHTBLUE = (0, 162, 232)
GRAY = (127, 127, 127)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

def distance_between_circles(point1, point2):
    # Distance between ball centers (pythagorean theorem)
    return math.sqrt((point1[0] - point2[0]) * (point1[0] - point2[0]) + (point1[1] - point2[1]) * (point1[1] - point2[1]))

def do_circles_overlap(point1, radius1, point2, radius2):   # check if circles overlap or touch (<=)
    return math.fabs((point1[0] - point2[0]) * (point1[0] - point2[0]) + (point1[1] - point2[1]) * (point1[1] - point2[1]) <= (radius1 + radius2) * (radius1 + radius2))
    # sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) < (r1+r2))           # takes long to compute, because of many square roots
    # fabs(x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) < (r1+r2)*(r1+r2)    # we can remove sqrt and look at absolute values instead for shorter computing time


class Ball():
    def __init__(self, px, py, radius, id, color):
        self.px = px                # point (x,y)
        self.py = py
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0                 # velocity vector (x,y) and acceleration vector (x,y)
   
        self.radius = radius
        self.id = id
        self.color = color
        self.img = pygame.transform.scale(pygame.image.load('assets/ball.png').convert_alpha(), (self.radius, self.radius))

        point_array = []
        n_points = 20
        for i in range(0, n_points):    # circle contains 20 segments, x and y of the points that lies on the circumference of the circle around the middle point
            point_array.append((math.cos(i / (n_points - 1) * 2 * math.pi), math.sin(i / (n_points - 1) * 2 * math.pi)))
            # { cosf(i / (float)(nPoints - 1) * 2.0f * 3.14159f), sinf(i / (float)(nPoints - 1) * 2.0f * 3.14159f) });
    
    def draw(self, screen):
        # When circle is image i can make it rotate around itself with angle math.atan2(self.velocity[0], self.velocity[1])
        self.img = pygame.transform.rotate(self.img, math.atan2(self.vx, self.vy))
        screen.blit(self.img, (self.px, self.py))
        # pygame.draw.circle(screen, self.color, self.point, self.radius)

    def gravity(self, floor_y):
        if floor_y > self.py + 33:
            self.py += 8
            
    
    def move(self, screen):
        pass



class Player(object):
    def __init__(self, x, y, radius, color):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.rect = pygame.draw.circle(SCREEN, self.color, (self.x, self.y), self.radius)
        self.in_air = True
        self.has_jumped = False
        self.jump_count = 20

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        rect_cut = pygame.Rect(self.x - self.radius, (self.y), self.radius*2, self.radius)
        pygame.draw.rect(screen, LIGHTBLUE, rect_cut)

    def gravity(self, floor_y):
        if floor_y > self.y:
            self.y += 10
            self.in_air = True
        else:
            self.in_air = False
            self.has_jumped = False
            self.jump_count = 20


    def move(self, key_pressed):
        if key_pressed[pygame.K_a] and self.x > self.radius:
            self.x -= 8
        elif key_pressed[pygame.K_d] and self.x < WIDTH - self.radius:
            self.x += 8

        if self.in_air and not key_pressed[pygame.K_w]:
            self.has_jumped = True

        if key_pressed[pygame.K_s] and self.in_air:
            self.y += 10
        elif not self.has_jumped and key_pressed[pygame.K_w] and self.jump_count > 0:
            self.y -= 20
            self.jump_count -= 1       


class Floor(object):
    def __init__(self):
        self.width = WIDTH
        self.height = 100
        self.y = HEIGHT - self.height
        self.floor_rect = pygame.Rect((0, self.y), (self.width, self.height))

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.floor_rect)


class Game(object):
    def __init__(self, arg):
        self.arg = arg
        self.clock = pygame.time.Clock()
        self.floor = Floor()
        self.player1 = Player(300, 600, 70, RED)
        self.ball = Ball(WIDTH/2, HEIGHT/2 + 100, 30, 1, WHITE)
        #self.player_group = pygame.sprite.Group()
        #self.player_group.add(self.player1)

    def draw_screen(self, screen):
        # bg < ball = (player < player_cut) < floor
        screen.fill(LIGHTBLUE)

        #player_group.draw(screen)
        self.player1.draw(screen)
        self.ball.draw(screen)
        self.floor.draw(screen)

    def main(self, SCREEN):
        clock = pygame.time.get_ticks()
        gamestate = 'RUNNING'

        """ Main Game Loop """
        while True:
            while gamestate == 'RUNNING':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                # Circle collision
                if do_circles_overlap((self.player1.x, self.player1.y), self.player1.radius, (self.ball.px, self.ball.py), self.ball.radius):
                    # Static Resolution
                    # Distance between ball centers
                    distance = distance_between_circles((self.player1.x, self.player1.y), (self.ball.px, self.ball.py))
                    
                    # Calculate the overlap (we only want half the overlap, because that is how much we want to displace)
                    overlap = 0.5 * (distance - self.ball.radius - self.player1.radius)
                    
                    # Displace Current ball - move away from player circle, by the amount of overlap in the direction the vector created in between the two balls
                    # we need to normalize this so it's sensible (by dividing by the distance between them)
                    self.ball.px -= overlap * (self.ball.px - self.player1.x) / distance
                    self.ball.py -= overlap * (self.ball.py - self.player1.y) / distance

                    # We can also displace the player for shockback
                    # self.player1.x += overlap * (self.ball.px - self.player1.x) / distance
                    # self.player1.y += overlap * (self.ball.py - self.player1.y) / distance

                # Dynamic collisions
                # Friction                          # https://www.youtube.com/watch?v=LPzyNOHY3A4&t=328s  -   24:00
                self.ball.ax -= self.ball.vx * 0.8
                self.ball.ay -= self.ball.vy * 0.8

                # Ball physics
                elapsed_time = self.clock.get_time()
                self.ball.vx += self.ball.ax * elapsed_time     # elapsed_time is length of previous frame
                self.ball.vy += self.ball.ay * elapsed_time
                self.ball.px += self.ball.vx * elapsed_time
                self.ball.py += self.ball.vy * elapsed_time

                if (math.fabs(self.ball.vx * self.ball.vx + self.ball.vy * self.ball.vy) < 0.1):    # stop the balls when moving slow enough
                    self.ball.vx = 0
                    self.ball.vy = 0
                

                # Gravity
                self.player1.gravity(self.floor.y)
                self.ball.gravity(self.floor.y)

                # Movement
                key_pressed = pygame.key.get_pressed()
                self.player1.move(key_pressed)

                # Draw
                self.draw_screen(SCREEN)

                pygame.display.update()
                self.clock.tick(60) # 60 fps

if __name__ == "__main__":
    Game(0).main(SCREEN)
