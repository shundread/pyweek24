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
    resources["realworld"] = resources["black"]

    # Background story
    set_text([
        "We run into the night",
        "with haste, escaping",
        "the blind monsters",
        "",
        "No matter how far we",
        "have to go, or what",
        "threats we face, I",
        "will protect us all",
    ])

def set_text(lines):
    surface = pygame.surface.Surface(Size)
    surface.fill(Black)
    font = pygame.font.SysFont("mono", 12, bold=True)

    for (n, line) in enumerate(lines):
        text = font.render(line, False, White)
        (w, h) = text.get_size()
        x = int((Width - w) * 0.5)
        y = int(Height * 0.2) + (n * h)
        surface.blit(text, (x, y))

    resources["text"] = surface

FadeInEnding = 1000
FadeOutEnding = FadeInEnding + 10000

def handle_key(game, data, event):
    data["miliseconds"] += FadeOutEnding

def simulate(game, data, dt):
    data["miliseconds"] += dt

    if data["miliseconds"] < FadeInEnding:
        resources["realworld"] = resources["black"]
    elif data["miliseconds"] < FadeOutEnding:
        resources["realworld"] = resources["text"]
    else:
        game.data["gamestate"] = "newtitle"

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

def handle_swap(game):
    init()
    game.data[""]
    pass
