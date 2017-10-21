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

    ################################
    # Render the real title screen #
    ################################
    title = pygame.surface.Surface(Size)
    title.fill(White)

    # Game title
    banner = pygame.image.load("data/titleC.png").convert_alpha()
    bannerwidth = banner.get_width()
    bannerx = int((Width - bannerwidth) * 0.5)
    bannery = int(Height * 0.2)
    title.blit(banner, (bannerx, bannery))

    # Game instructions
    font = pygame.font.SysFont("mono", 12, bold=True)
    lines = [
        "move around with 'WASD'",
        "aim flashlight with mouse",
        "interact with 'E'",
        "break open with 'R'",
        "",
        "press 'I' to start"
    ]
    for (n, line) in enumerate(lines):
        text = font.render(line, False, Black)
        (w, h) = text.get_size()
        x = int((Width - w) * 0.5)
        y = int(Height * 0.5) + (n * h)
        title.blit(text, (x, y))

    resources["title"] = title

    ############################
    # Render the opening quote #
    ############################
    quote = pygame.surface.Surface(Size)
    quote.fill(Black)
    lines = [
        "\"family means no one",
        "gets left behind or",
        "forgotten\"",
        "",
        "-David Ogden Stiers"
    ]
    for (n, line) in enumerate(lines):
        text = font.render(line, False, White)
        (w, h) = text.get_size()
        x = int((Width - w) * 0.5)
        y = int(Height * 0.3) + (n * h)
        quote.blit(text, (x, y))

    resources["quote"] = quote
    resources["realworld"] = quote

FadeInQuote = 1000
FadeOutQuote = FadeInQuote + 5000

def handle_key(game, data, event):
    data["miliseconds"] += FadeOutQuote
    if (event.key == pygame.K_i):
        game.data["gamestate"] = "newintro"


def simulate(game, data, dt):
    data["miliseconds"] += dt

    if data["miliseconds"] < FadeInQuote:
        resources["realworld"] = resources["black"]
    elif data["miliseconds"] < FadeOutQuote:
        resources["realworld"] = resources["quote"]
    else:
        resources["realworld"] = resources["title"]

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
    game.data["title"] = reset_data()
