import pygame
import random

resources = {}

Black = (0, 0, 0)
White = (255, 255, 255)

def reset_data():
    return {
        "miliseconds": 0,
        "position": {
            "x": 50,
            "y": 50,
        },
    }

def init():
    screen = pygame.display.get_surface()
    resources["vision"] = pygame.surface.Surface((200, 200))
    resources["realworld"] = pygame.surface.Surface((200, 200))
    pygame.transform.scale(screen, (200, 200), resources["vision"])

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
    realworld = resources["realworld"]
    realworld.fill(White)

    position = (data["position"]["x"], data["position"]["y"])
    pygame.draw.rect(realworld, Black, (position, (20, 20)))

    vision = resources["vision"]
    (width, height) = vision.get_size()
    for p in range(800):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        color = realworld.get_at((x, y))
        vision.set_at((x, y), color)

    screen = pygame.display.get_surface()
    pygame.transform.scale(vision, screen.get_size(), screen)
    pygame.display.flip()

def handle_swap(game):
    init()
