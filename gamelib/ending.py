import pygame
# import numpy

Black = (0, 0, 0)
White = (255, 255, 255)
Size = (Width, Height) = (200, 200)
Pass = 0.25

EndingTexts = {
    0: [
        "As the blind beast",
        "eats my flesh, I am",
        "filled with terror",
        "",
        "The world goes dark,",
        "and then there is",
        "nothing",
    ],
    1: [
        "Unable to save anyone",
        "else, I run away and",
        "cry in shame",
        "",
        "Lost and alone, I find",
        "myself hopeless and",
        "certain that it will",
        "not be long before",
        "the beasts follow me",
    ],
    2: [
        "The two of us escape",
        "the area with pain in",
        "our hearts",
        "",
        "We are not sure how",
        "we are going to manage",
        "out there, but we will",
        "try our best"
    ],
    3: [
        "We run into the night",
        "quietly and hastily,",
        "escaping the monsters",
        "",
        "No matter how far we",
        "have to go, or what",
        "threats we face, I",
        "will protect us all",
    ]
}

def reset_data():
    return { "miliseconds": 0 }

resources = {}

def init():
    screen = pygame.display.get_surface()

    # resources["scatter"] = numpy.random.random(Size)
    resources["vision"] = pygame.surface.Surface(Size)
    pygame.transform.scale(screen, Size, resources["vision"])

    ###########################
    # Render the black screen #
    ###########################
    resources["black"] = pygame.surface.Surface(Size)
    resources["black"].fill(Black)
    resources["realworld"] = resources["black"]

    # Background story
    set_text(EndingTexts[3])

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
    # scatter = resources["scatter"]
    # numpy.random.shuffle(scatter)
    # for x in range(Width):
    #     for y in range(Height):
    #         if scatter[x, y] < Pass:
    #             color = realworld.get_at((x, y))
    #             vision.set_at((x, y), color)

    screen = pygame.display.get_surface()
    pygame.transform.scale(realworld, screen.get_size(), screen)
    pygame.display.flip()

def handle_swap(game):
    init()
    game.data[""]
    pass
