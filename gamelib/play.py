import pygame
import numpy
import math
import random
import mapgenerator

Black = (0, 0, 0)
White = (255, 255, 255)
Size = (Width, Height) = (200, 200)
Pass = 0.40
HalfConeAngle = 0.20 * math.pi
Shadow = White
ShadowAlpha = 255
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

PositionScale = 20

# Collision box sizes
BoxPerson = 12 * PositionScale
DistanceRescue = 30 * PositionScale
DistanceFollow = 28 * PositionScale

# Speeds
SpeedPerson = 2

def reset_data():
    return {
        "miliseconds": 0,
        "player": {
            "position": (0, 0),
            "next_position": (0, 0),
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
    for (n, (x, y)) in enumerate(game_data["map"]["family_spawns"]):
        game_data["characters"].append({
            "position": (x * PositionScale, y * PositionScale),
            "next_position": (x * PositionScale, y * PositionScale),
            "angle": n,
            "state": "hiding",
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

    player = game_data["player"]
    player_position = (px, py) = get_position(player)

    # Simulate characters
    characters = game_data["characters"]
    for character in characters:
        position = (x, y) = character["position"]
        distance = point_point_distance(player_position, position)
        if character["state"] == "hiding":
            if distance < DistanceRescue:
                character["state"] = "following"

        if character["state"] == "following":
            (dx, dy) = (px - x, py - y)
            angle = math.atan2(dy, dx)
            character["angle"] = angle
            if distance > DistanceFollow:
                dx = math.copysign(min(abs(dx), dt * SpeedPerson), dx)
                dy = math.copysign(min(abs(dy), dt * SpeedPerson), dy)
                set_next_position(character, (x + dx, y + dy))

    # Collide characters with each other
    all_characters = characters + [player]
    for (i, c0) in enumerate(characters):
        for c1 in all_characters:
            if c0 == c1:
                continue
            (x0, y0) = p0 = get_next_position(c0)
            (x1, y1) = p1 = get_next_position(c1)

            distance = point_point_distance(p0, p1)
            if distance < BoxPerson:
                (dx, dy) = (x1 - x0, y1 - y0)
                angle = math.atan2(dy, dx)
                depth = BoxPerson - distance
                pushback = 0.5 * depth

                nx0 = x0 - math.cos(angle) * pushback
                ny0 = y0 - math.sin(angle) * pushback
                nx1 = x1 + math.cos(angle) * pushback
                ny1 = y1 + math.sin(angle) * pushback
                set_next_position(c0, (nx0, ny0))
                set_next_position(c1, (nx1, ny1))

    # The player never gets pushed around, only killed :)
    (dx, dy) = (0, 0)
    if keys[pygame.K_w]: dy -= SpeedPerson * dt
    if keys[pygame.K_s]: dy += SpeedPerson * dt
    if keys[pygame.K_a]: dx -= SpeedPerson * dt
    if keys[pygame.K_d]: dx += SpeedPerson * dt
    set_next_position(player, (px + dx, py + dy))

    # Collide characters with walls
    area_map = game_data["map"]
    buildings = area_map["structures"]

    line_barriers = buildings["doors"] + buildings["walls"]
    barrier_rects = []
    for unscaled_line in line_barriers:
        scaled_line = [v * PositionScale for v in unscaled_line]
        barrier_rects.append(line_to_rect(*scaled_line))

    for character in game_data["characters"] + [player]:
        (x, y) = get_position(character)
        (x1, y1) = get_next_position(character)
        (dx, dy) = (x1 - x, y1 - y)
        crect = pygame.rect.Rect(0, 0, BoxPerson, BoxPerson)

        for lrect in barrier_rects:
            # Collide horizontal
            if dx:
                crect.center = (x + dx, y)
                collision = rects_collision(crect, lrect)
                if collision[0]:
                    if dx > 0:
                        crect.right = lrect.left
                    else:
                        crect.left = lrect.right

                    dx = crect.centerx - x

            # Collide vertical
            if dy:
                crect.center = (x, y + dy)
                collision = rects_collision(crect, lrect)
                if collision[1]:
                    if dy > 0:
                        crect.bottom = lrect.top
                    else:
                        crect.top = lrect.bottom
                    dy = crect.centery - y

        set_position(character, (x + dx, y + dy))
        set_next_position(character, (x + dx, y + dy))

def point_point_distance((x0, y0), (x1, y1)):
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

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
    player_position = (px, py) = get_render_position(game_data["player"])
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
        position = get_render_position(character)
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

def get_render_position(entity):
    (x, y) = entity["position"]
    return (
        int(round(float(x) / PositionScale)),
        int(round(float(y) / PositionScale))
    )

def get_position(entity):
    return entity["position"]

def set_position(entity, (x, y)):
    entity["position"] = (x, y)

def get_next_position(entity):
    return entity["next_position"]

def set_next_position(entity, (x, y)):
    entity["next_position"] = (x, y)
