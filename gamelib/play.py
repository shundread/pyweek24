import pygame
import numpy
import math
import random
import mapgenerator

Black = (0, 0, 0)
White = (255, 255, 255)
Size = (Width, Height) = (600, 600)
Pass = 0.40
HalfConeAngle = 0.20 * math.pi
Shadow = White
ShadowAlpha = 128
ShadowLength = Width * 2

# Colors
ColorDoor = (140, 110, 0)
ColorWall = (128, 128, 128)
ColorWindow = (0, 0, 255)
ColorHead = (200, 200, 0)
ColorShirt = (30, 200, 40)

# Entity size info
SizeHead = 4
SizeShoulder = 4

# Collision box sizes
BoxPerson = 12

def reset_data():
    return {
        "miliseconds": 0,
        "player": {
            "position": (0, 0),
        },
        "characters": []
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

def generate_map(game_data):
    mapgenerator.generate_map(game_data)

    # Place the family members
    game_data["characters"] = []
    for (n, position) in enumerate(game_data["map"]["family_spawns"]):
        game_data["characters"].append({
            "position": position,
            "angle": n
        })

    # Place the monsters
    # TODO

    generate_minimap()

def generate_minimap():
    pass

def handle_key(game, game_data, event):
    if (event.key == pygame.K_ESCAPE):
        game.data["gamestate"] = "newtitle"
    if (event.key == pygame.K_m):
        generate_map(game_data)

def simulate(game, game_data, dt):
    game_data["miliseconds"] += dt
    keys = pygame.key.get_pressed()

    player_position = (px, py) = get_player_position(game_data)
    (dx, dy) = (0, 0)
    # TODO make speed adjustable to dt, and scale player position in the getter
    if keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_s]: dy += 1
    if keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_d]: dx += 1

    area_map = game_data["map"]
    buildings = area_map["structures"]
    line_barriers = buildings["doors"] + buildings["walls"]
    prect = pygame.rect.Rect(0, 0, BoxPerson, BoxPerson)
    for (x0, y0, x1, y1) in line_barriers:
        lrect = line_to_rect(x0, y0, x1, y1)

        # Collide horizontal
        prect.center = (px + dx, py)
        collision = rects_collision(prect, lrect)
        dx = math.copysign(abs(dx) - collision[0], dx)

        # Collide vertical
        prect.center = (px, py + dy)
        collision = rects_collision(prect, lrect)
        dy = math.copysign(abs(dy) - collision[1], dy)
    set_player_position(game_data, (int(px + dx), int(py + dy)))

def line_to_rect(x0, y0, x1, y1):
    x = min(x0, x1)
    y = min(y0, y1)
    w = max(x0, x1) - x
    h = max(y0, y1) - y
    return pygame.rect.Rect(x-2, y-2, w+4, h+4)

def rects_collision(r1, r2):
    return r1.clip(r2).size

def render(game_data):
    # Renders the real world
    realworld = resources["realworld"]
    realworld.fill(Black)
    area_map = game_data["map"]

    mouse_offset = (mdx, mdy) = get_mouse_offset()
    mouse_angle = get_mouse_angle(mdx, mdy)
    player_position = (px, py) = get_player_position(game_data)
    camera = (cx, cy) = (
        px + int(0.3 * mdx - 0.5 * Width),
        py + int(0.3 * mdy - 0.5 * Height)
    )

    # Renders the player and the light surface
    light = resources["light"]
    light.fill(Black)
    # light.fill(White)d
    # drawpoly(light, Black, camera, [
    #     player_position,
    #     (
    #         px + math.cos(mouse_angle + HalfConeAngle) * ShadowLength,
    #         py + math.sin(mouse_angle + HalfConeAngle) * ShadowLength,
    #     ),
    #     (
    #         px + math.cos(mouse_angle - HalfConeAngle) * ShadowLength,
    #         py + math.sin(mouse_angle - HalfConeAngle) * ShadowLength,
    #     ),
    # ])

    for floor in area_map["structures"]["floors"]:
        (x, y, w, h, r, g, b) = floor
        drawrect(realworld, (r, g, b), camera, (x, y, w, h))

    # Draw the player
    drawcharacter(realworld, ColorHead, ColorShirt, camera, player_position, mouse_angle)

    # Draw the other characters
    for character in game_data["characters"]:
        position = character["position"]
        angle = character["angle"]
        drawcharacter(realworld, ColorHead, ColorShirt, camera, position, angle)

    # TODO draw the monsters

    for wall in area_map["structures"]["walls"]:
        (x0, y0, x1, y1) = wall
        drawline(realworld, ColorWall, camera, (x0, y0), (x1, y1), 5)
        cast_shadow(light, Shadow, camera, player_position, wall)

    for door in area_map["structures"]["doors"]:
        (x0, y0, x1, y1) = door
        drawline(realworld, ColorDoor, camera, (x0, y0), (x1, y1), 5)
        cast_shadow(light, Shadow, camera, player_position, door)

    for window in area_map["structures"]["windows"]:
        (x0, y0, x1, y1) = window
        drawline(realworld, ColorWindow, camera, (x0, y0), (x1, y1), 5)

    # Apply the light to the surface
    light.set_alpha(ShadowAlpha)
    realworld.blit(light, (0, 0))

    # TODO: cpu-friendly funky vision updates

    # Renders the realworld (or the vision, if we got that far with the project)
    screen = pygame.display.get_surface()
    pygame.transform.scale(realworld, screen.get_size(), screen)
    pygame.display.flip()

def drawcircle(surface, color, (cx, cy), (x, y), radius):
    pygame.draw.circle(surface, color, (x - cx, y - cy), radius)

def drawrect(surface, color, (cx, cy), (x, y, w, h)):
    pygame.draw.rect(surface, color, ((x - cx, y - cy), (w, h)))

def drawline(surface, color, (cx, cy), (x0, y0), (x1, y1), width):
    pygame.draw.line(surface, color, (x0 - cx, y0 - cy), (x1 - cx, y1 - cy), width)

def drawpoly(surface, color, (cx, cy), points):
    transposed = [(x - cx, y - cy) for (x, y) in points]
    pygame.draw.polygon(surface, color, transposed)

def drawcharacter(surface, color_head, color_shirt, camera, position, angle):
    (px, py) = position
    shoulder_left = (
        px + int(4 * math.sin(angle)),
        py - int(4 * math.cos(angle)),
    )
    shoulder_right = (
        px - int(4 * math.sin(angle)),
        py + int(4 * math.cos(angle)),
    )
    drawcircle(surface, color_shirt, camera, shoulder_left, 4)
    drawcircle(surface, color_shirt, camera, shoulder_right, 4)
    drawcircle(surface, color_shirt, camera, position, 5)
    drawcircle(surface, color_head, camera, position, 4)

def cast_shadow(surface, color, camera, (lx, ly), (x1, y1, x2, y2)):
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

def get_mouse_offset():
    screen = pygame.display.get_surface()
    (w, h) = screen.get_size()
    (x, y) = pygame.mouse.get_pos()
    dx = x - (w * 0.5)
    dy = y - (h * 0.5)
    return (dx, dy)

def get_mouse_angle(dx, dy):
    return math.atan2(dy, dx)

def get_player_position(game_data):
    return game_data["player"]["position"]

def set_player_position(game_data, (x, y)):
    game_data["player"]["position"] = (x, y)
