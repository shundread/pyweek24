import pygame
import numpy
import math
import random

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

MinimumBuildings = 4
MaximumBuildings = 7
LotSize = (LotWidth, LotHeight) = (10, 10)
TileSize = (TileWidth, TileHeight) = (2, 2)
def generate_map(game_data):
    area = {}

    # Generate the lot "vacancies" and shuffle them for assignment of the areas
    vacant_lots = []
    for lotx in [-1, 0, 1]:
        for loty in [-1, 0, 1]:
            vacant_lots.append((lotx, loty))
    random.shuffle(vacant_lots)

    # Pick lots at random and generate buildings on them
    n_buildings = random.randint(MinimumBuildings, MaximumBuildings)
    buildings = []
    for b in range(n_buildings):
        (x, y) = vacant_lots.pop()
        # TODO store polygons
        buildings.append((
            x * LotWidth * TileWidth,
            y * LotHeight * TileHeight,
            int(LotWidth * 0.8) * TileWidth,
            int(LotHeight * 0.8) * TileHeight
        ))
    area["buildings"] = buildings

    # Generate open area on the remaining lots
    while len(vacant_lots) > 0:
        lot = vacant_lots.pop()

    game_data["map"] = area

def handle_key(game, data, event):
    if (event.key == pygame.K_ESCAPE):
        game.data["gamestate"] = "newtitle"
    if (event.key == pygame.K_m):
        generate_map(data)

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
    ppos = (px, py) = (data["position"]["x"], data["position"]["y"])

    area_map = data["map"]
    for building in area_map["buildings"]:
        (x, y, w, h) = building
        pygame.draw.rect(realworld, White, (x - px, y - py, w, h))

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
    # realworld.blit(light, (0, 0))

    screen = pygame.display.get_surface()
    pygame.transform.scale(realworld, screen.get_size(), screen)
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
