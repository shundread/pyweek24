import pygame
import numpy
import math

Black = (0, 0, 0)
White = (255, 255, 255)
Size = (Width, Height) = (200, 200)
Pass = 0.40
HalfConeAngle = 0.15 * math.pi

def reset_data():
    return {
        "miliseconds": 0,
        "position": {
            "x": 50,
            "y": 50,
        },
    }

resources = {}

def init():
    screen = pygame.display.get_surface()
    resources["scatter"] = numpy.random.random(Size)
    resources["realworld"] = pygame.surface.Surface(Size)

    resources["light"] = pygame.surface.Surface(Size)
    resources["light"].convert()
    resources["light"].set_colorkey(Black)

    resources["hud"] = pygame.surface.Surface(Size)

    resources["vision"] = pygame.surface.Surface(Size)
    pygame.transform.scale(screen, Size, resources["vision"])

def handle_key(game, data, event):
    if (event.key == pygame.K_ESCAPE):
        game.data["gamestate"] = "newtitle"

def simulate(game, data, dt):
    data["miliseconds"] += dt
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]: data["position"]["y"] -= 1
    if keys[pygame.K_s]: data["position"]["y"] += 1
    if keys[pygame.K_a]: data["position"]["x"] -= 1
    if keys[pygame.K_d]: data["position"]["x"] += 1

def render(data):
    # Renders the real world
    realworld = resources["realworld"]
    realworld.fill(Black)
    position = (data["position"]["x"], data["position"]["y"])
    pygame.draw.rect(realworld, White, (position, (20, 20)))

    # Renders the light surface
    center = (middlex, middley) = (Width * 0.5, Height * 0.5)
    angle = get_mouse_angle()
    light = resources["light"]
    light.fill(White)
    pygame.draw.polygon(light, Black, [
        center,
        (
            middlex * math.cos(angle + HalfConeAngle) * 100,
            middley * math.sin(angle + HalfConeAngle) * 100
        ),
        (
            middlex * math.cos(angle - HalfConeAngle) * 100,
            middley * math.sin(angle - HalfConeAngle) * 100
        )
    ])

    # Apply the light to the surface
    realworld.blit(light, (0, 0))

    vision = resources["vision"]
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

def get_mouse_angle():
    screen = pygame.display.get_surface()
    (w, h) = screen.get_size()
    (x, y) = pygame.mouse.get_pos()
    dx = x - (w * 0.5)
    dy = y - (h * 0.5)
    return math.atan2(dy, dx)
