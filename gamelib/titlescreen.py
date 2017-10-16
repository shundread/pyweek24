import pygame
import tween
import random

resources = {}

def reset_data():
    return {
        "miliseconds": 0,
        "background_color": (0, 0, 0),
    }

def init():
    screen = pygame.display.get_surface()
    resources["title"] = pygame.image.load("data/titleC.png").convert_alpha()
    resources["background"] = pygame.surface.Surface((200, 200))
    pygame.transform.scale(screen, (200, 200), resources["background"])
    resources["background"].fill((0, 0, 0))
    font = pygame.font.SysFont("mono", 12, bold=True)
    lines = [
        "move around with 'WASD'",
        "interact with 'E'",
        "fire with space",
        "",
        "press 'x' to start"
    ]
    resources["instructions"] = []
    for line in lines:
        resources["instructions"].append(font.render(line, False, (0, 0, 0)))

def handle_key(game, data, event):
    if (event.key == pygame.K_x):
        game.data["gamestate"] = "newgame"

FadeIn = 4000.0

def simulate(game, data, dt):
    data["miliseconds"] += dt

    miliseconds = data["miliseconds"]

    if miliseconds < FadeIn:
        data["background_color"] = (0, 0, 0)
    else:
        data["background_color"] = (255, 255, 255)


def render(data):
    color = data["background_color"]
    bg = resources["background"]
    (width, height) = bg.get_size()

    for p in range(200):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        bg.set_at((x, y), color)

    title = resources["title"]
    titlewidth = title.get_width()
    titlex = int((width - titlewidth) * 0.5)
    titley = int(height * 0.25)
    bg.blit(title, (titlex, titley))

    instructions = resources["instructions"]
    for (n, line) in enumerate(instructions):
        linewidth = line.get_width()
        lineheight = line.get_height() * n
        linex = int((width - linewidth) * 0.5)
        liney = int(height * 0.6) + lineheight
        bg.blit(line, (linex, liney))

    screen = pygame.display.get_surface()
    pygame.transform.scale(bg, screen.get_size(), screen)

    pygame.display.flip()

def handle_swap(game):
    reload(tween)
    init()
    game.data["title"] = reset_data()
