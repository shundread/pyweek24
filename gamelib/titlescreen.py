import pygame
import tween
import random

resources = {}

Black = (0, 0, 0)
White = (255, 255, 255)

def reset_data():
    return {
        "miliseconds": 0,
        "background_color": Black,
    }

def init():
    screen = pygame.display.get_surface()

    size = (width, height) = (200, 200)
    resources["vision"] = pygame.surface.Surface(size)
    pygame.transform.scale(screen, size, resources["vision"])

    ################################
    # Render the real title screen #
    ################################
    realworld = pygame.surface.Surface(size)
    realworld.fill(White)

    # Game title
    title = pygame.image.load("data/titleC.png").convert_alpha()
    titlewidth = title.get_width()
    titlex = int((width - titlewidth) * 0.5)
    titley = int(height * 0.25)
    realworld.blit(title, (titlex, titley))

    # Game instructions
    font = pygame.font.SysFont("mono", 12, bold=True)
    lines = [
        "move around with 'WASD'",
        "interact with 'E'",
        "fire with space",
        "",
        "press 'x' to start"
    ]
    for (n, line) in enumerate(lines):
        text = font.render(line, False, Black)
        (w, h) = text.get_size()
        x = int((width - w) * 0.5)
        y = int(height * 0.6) + (n * h)
        realworld.blit(text, (x, y))

    resources["realworld"] = realworld

def handle_key(game, data, event):
    if (event.key == pygame.K_x):
        game.data["gamestate"] = "newgame"

FadeIn = 4000.0

def simulate(game, data, dt):
    data["miliseconds"] += dt

def render(data):
    vision = resources["vision"]
    (width, height) = vision.get_size()
    if data["miliseconds"] < FadeIn:
        for p in range(200):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            vision.set_at((x, y), Black)

    else:
        realworld = resources["realworld"]
        for p in range(200):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            color = realworld.get_at((x, y))
            vision.set_at((x, y), color)

    screen = pygame.display.get_surface()
    pygame.transform.scale(vision, screen.get_size(), screen)
    pygame.display.flip()

def handle_swap(game):
    reload(tween)
    init()
    game.data["title"] = reset_data()
