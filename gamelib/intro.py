import pygame
import numpy

Black = (0, 0, 0)
White = (255, 255, 255)
Size = (Width, Height) = (200, 200)
Pass = 0.25

def reset_data():
    return { "miliseconds": 0 }

resources = {}

def init():
    screen = pygame.display.get_surface()

    resources["scatter"] = numpy.random.random(Size)
    resources["vision"] = pygame.surface.Surface(Size)
    pygame.transform.scale(screen, Size, resources["vision"])

    ###########################
    # Render the black screen #
    ###########################
    resources["black"] = pygame.surface.Surface(Size)
    resources["black"].fill(Black)

     ###########################
    # Render the intro screen #
    ###########################
    intro = pygame.surface.Surface(Size)
    intro.fill(Black)

    # Background story
    font = pygame.font.SysFont("mono", 12, bold=True)
    lines = [
        "A strange darkness has",
        "descended into the area",
        "",
        "Blind monsters are roaming",
        "about, listening for prey",
        "",
        "I must find my family and",
        "quietly lead safely to the",
        "exit on the south"
    ]
    for (n, line) in enumerate(lines):
        text = font.render(line, False, White)
        (w, h) = text.get_size()
        x = int((Width - w) * 0.5)
        y = int(Height * 0.2) + (n * h)
        intro.blit(text, (x, y))
    resources["intro"] = intro

FadeInIntro = 1000
FadeOutIntro = FadeInIntro + 10000

def handle_key(game, data, event):
    data["miliseconds"] += FadeOutIntro

def simulate(game, data, dt):
    data["miliseconds"] += dt

    if data["miliseconds"] < FadeInIntro:
        resources["realworld"] = resources["black"]
    elif data["miliseconds"] < FadeOutIntro:
        resources["realworld"] = resources["intro"]
    else:
        game.data["gamestate"] = "newgame"

def render(data):
    vision = resources["vision"]
    (width, height) = vision.get_size()

    realworld = resources["realworld"]
    scatter = resources["scatter"]
    numpy.random.shuffle(scatter)
    for x in range(Width):
        for y in range(Height):
            if scatter[x, y] < Pass:
                color = realworld.get_at((x, y))
                vision.set_at((x, y), color)

    screen = pygame.display.get_surface()
    pygame.transform.scale(vision, screen.get_size(), screen)
    pygame.display.flip()
