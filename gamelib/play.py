import pygame
import numpy
import math
import random
import mapgenerator

Black = (0, 0, 0)
White = (255, 255, 255)
Size = (Width, Height) = (200, 200)
Pass = 0.40
HalfConeAngle = 0.15 * math.pi
Shadow = (255, 0, 0)
ShadowLength = 300

# Thing colors
ColorDoor = (140, 110, 0)

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

def generate_map(data):
    mapgenerator.generate_map(data)

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
    area_map = data["map"]

    player_position = (px, py) = (data["position"]["x"], data["position"]["y"])
    camera = (cx, cy) = (px - Width * 0.5, py - Height * 0.5)
    mouse_angle = get_mouse_angle()

    # Renders the light surface
    light = resources["light"]
    light.fill(White)
    drawpoly(light, Black, camera, [
        player_position,
        (
            px + math.cos(mouse_angle + HalfConeAngle) * ShadowLength,
            py + math.sin(mouse_angle + HalfConeAngle) * ShadowLength,
        ),
        (
            px + math.cos(mouse_angle - HalfConeAngle) * ShadowLength,
            py + math.sin(mouse_angle - HalfConeAngle) * ShadowLength,
        ),
    ])


    for room in area_map["buildings"]["floors"]:
        (x, y, w, h, r, g, b) = room
        pygame.draw.rect(realworld, (r, g, b), ((x - cx, y - cy), (w, h)))

    for wall in area_map["buildings"]["walls"]:
        (x0, y0, x1, y1) = wall
        drawline(realworld, White, camera, (x0, y0), (x1, y1), 3)
        cast_shadow(light, camera, player_position, wall, Shadow)

    for door in area_map["buildings"]["doors"]:
        (x0, y0, x1, y1) = door
        #pygame.draw.line(realworld, ColorDoor, (x0 - px, y0 - py), (x1 - px, y1 - py), 3)
        #cast_shadow(light, center, wall, Shadow)

    for window in area_map["buildings"]["windows"]:
        (x0, y0, x1, y1) = window
        #pygame.draw.line(realworld, (0, 0, 255), (x0 - px, y0 - py), (x1 - px, y1 - py), 3)

    # Apply the light to the surface
    light.set_alpha(128)
    realworld.blit(light, (0, 0))

    screen = pygame.display.get_surface()
    pygame.transform.scale(realworld, screen.get_size(), screen)
    pygame.display.flip()

def drawline(surface, color, (cx, cy), (x0, y0), (x1, y1), width):
    pygame.draw.line(surface, color, (x0 - cx, y0 - cy), (x1 - cx, y1 - cy), width)

def drawpoly(surface, color, (cx, cy), points):
    transposed = [(x - cx, y - cy) for (x, y) in points]
    pygame.draw.polygon(surface, color, transposed)

def cast_shadow(surface, camera, (lx, ly), (x1, y1, x2, y2), color):
    dy = y1 - ly
    dx = x1 - lx
    angle1 = math.atan2(dy, dx)

    dy = y2 - ly
    dx = x2 - lx
    angle2 = math.atan2(dy, dx)

    drawpoly(surface, color, camera, [
        (x1, y1),
        (x1 + math.cos(angle1) * ShadowLength, y1 + math.sin(angle1) * ShadowLength),
        (x2 + math.cos(angle2) * ShadowLength, y2 + math.sin(angle2) * ShadowLength),
        (x2, y2)
    ])

def handle_swap(game):
    init()
    reload(mapgenerator)

def get_mouse_angle():
    screen = pygame.display.get_surface()
    (w, h) = screen.get_size()
    (x, y) = pygame.mouse.get_pos()
    dx = x - (w * 0.5)
    dy = y - (h * 0.5)
    return math.atan2(dy, dx)
