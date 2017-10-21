import pygame
import numpy
import math
import random
import mapgenerator

# Colors
Black = (0, 0, 0)
White = (255, 255, 255)
ColorDoor = (140, 110, 0)
ColorWall = (128, 128, 128)
ColorWindow = (0, 0, 255)
ColorHead = (200, 200, 0)
ColorShirt = (30, 200, 40)

# Surface info
Size = (Width, Height) = (200, 200)

# Minimap info
MinimapSize = (MinimapWidth, MinimapHeight) = (int(Width * 0.15), int(Height * 0.15))
MinimapMargin = (int(MinimapWidth * 0.5), int (MinimapHeight * 0.5))
MinimapAlpha = 128
MinimapForeground = (160, 240, 80)
MinimapBackground = (60, 100, 150)
MinimapPersonIndicator = (20, 0, 20)

# Light parameters
HalfConeAngle = 0.20 * math.pi
Shadow = White
ShadowAlpha = 128
ShadowLength = Width * 20

# Funky update parameters (UNUSED)
Pass = 0.40

# Entity size info
SizeHead = 4
SizeShoulder = 4

ScalePosition = 20

# Collision box sizes
BoxPerson = 12 * ScalePosition

# Distances
DistanceRescue = 30 * ScalePosition
DistanceFollow = 28 * ScalePosition
DistanceInteract = 20 * ScalePosition

# Speeds
SpeedPerson = 4

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

    resources["minimap"] = pygame.surface.Surface(MinimapSize)
    resources["minimap"].convert()
    resources["minimap"].set_alpha(MinimapAlpha)

    resources["light"] = pygame.surface.Surface(Size)
    resources["light"].convert()
    resources["light"].set_colorkey(Black)
    resources["light"].set_alpha(ShadowAlpha)

    resources["hud"] = pygame.surface.Surface(Size)

    resources["vision"] = pygame.surface.Surface(Size)
    pygame.transform.scale(screen, Size, resources["vision"])

def generate_map(game_data):
    mapgenerator.generate_map(game_data)

    # Place the player & other family members
    family_spawns = game_data["map"]["family_spawns"]
    (x, y) = family_spawns.pop()
    set_position(game_data["player"], (x * ScalePosition, y * ScalePosition))

    game_data["characters"] = []
    for (n, (x, y)) in enumerate(game_data["map"]["family_spawns"]):
        game_data["characters"].append({
            "position": (x * ScalePosition, y * ScalePosition),
            "next_position": (x * ScalePosition, y * ScalePosition),
            "angle": n,
            "state": "hiding",
        })


    # Place the monsters
    # TODO


def draw_minimap(game_data):
    minimap = resources["minimap"]
    minimap.fill(MinimapBackground)
    fullwidth = float(mapgenerator.MapWidth)
    fullheight = float(mapgenerator.MapHeight)
    xscale = (MinimapWidth) / fullwidth
    yscale = (MinimapHeight) / fullheight
    area_map = game_data["map"]
    for floor in area_map["structures"]["buildings"]:
        rect = pygame.rect.Rect(*floor[0:4])
        rect.left = int(math.floor(rect.left * xscale))
        rect.top = int(math.floor(rect.top * yscale))
        rect.width = int(math.ceil(rect.width * xscale))
        rect.height = int(math.ceil(rect.height * yscale))
        pygame.draw.rect(minimap, MinimapForeground, rect)

    (x, y) = get_render_position(game_data["player"])
    xs = int(math.floor(x * xscale))
    ys = int(math.floor(y  * yscale))
    minimap.set_at((xs, ys), MinimapPersonIndicator)

def handle_key(game, game_data, event):
    if (event.key == pygame.K_ESCAPE):
        game.data["gamestate"] = "newtitle"
    if (event.key == pygame.K_e):
        interact(game_data)
    if (event.key == pygame.K_r):
        force_open(game_data)
    if (event.key == pygame.K_m):
        generate_map(game_data)

def interact(game_data):
    structures = game_data["map"]["structures"]
    doors = structures["doors"]
    windows = structures["windows"]
    if not open_passage(game_data, doors, force=False):
        open_passage(game_data, windows, force=False)

def force_open(game_data):
    structures = game_data["map"]["structures"]
    doors = structures["doors"]
    windows = structures["windows"]
    if not open_passage(game_data, doors, force=True):
        open_passage(game_data, windows, force=True)

def open_passage(game_data, passages, force):
    player_position = get_position(game_data["player"])
    for (i, item) in enumerate(passages):
        (x0, y0, x1, y1, locked) = item
        (x, y) = (0.5 * ScalePosition * (x0 + x1), 0.5 * ScalePosition * (y0 + y1))
        distance = point_point_distance(player_position, (x, y))
        if distance < DistanceInteract:
            if force:
                print "forcing open the thing"
                passages.pop(i)
                return True

            if locked:
                print "cannot open thing"
                return True
            else:
                print "opening the thing"
                passages.pop(i)
                return True

def simulate(game, game_data, dt):
    game_data["miliseconds"] += dt
    keys = pygame.key.get_pressed()

    player = game_data["player"]
    player_position = (px, py) = get_position(player)

    if check_game_over(game, game_data):
        return

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
    structures = area_map["structures"]

    line_barriers = \
        structures["windows"] + \
        structures["doors"] + \
        structures["walls"] + \
        area_map["limits"]

    barrier_rects = []
    for unscaled_line in line_barriers:
        scaled_line = [v * ScalePosition for v in unscaled_line[0:4]]
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
                crect.center = (x + dx, y + dy)
                collision = rects_collision(crect, lrect)
                if collision[1]:
                    if dy > 0:
                        crect.bottom = lrect.top
                    else:
                        crect.top = lrect.bottom
                    dy = crect.centery - y

        set_position(character, (x + dx, y + dy))
        set_next_position(character, (x + dx, y + dy))

def check_game_over(game, game_data):
    (x, y) = get_render_position(game_data["player"])
    if y > mapgenerator.MapHeight + 100:
        game.data["gamestate"] = "newending"
        return True

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

    screen_rect = pygame.rect.Rect((0, 0), (Width + 20, Height + 20))
    screen_rect.topleft = camera
    screen_rect.top -= 10
    screen_rect.left -= 10

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

    # Draw the other characters
    for character in game_data["characters"]:
        position = get_render_position(character)
        angle = character["angle"]
        drawcharacter(realworld, ColorHead, ColorShirt, camera, position, angle)

    # TODO draw the monsters

    # Draw the player
    drawcharacter(realworld, ColorHead, ColorShirt, camera, player_position, mouse_angle)

    for wall in area_map["structures"]["walls"]:
        (x0, y0, x1, y1) = wall
        wrect = line_to_rect(x0, y0, x1, y1)
        if not screen_rect.colliderect(wrect):
            continue
        drawline(realworld, ColorWall, camera, (x0, y0), (x1, y1), 5)
        cast_shadow(light, Shadow, camera, player_position, wall)

    for door in area_map["structures"]["doors"]:
        (x0, y0, x1, y1, locked) = door
        wrect = line_to_rect(x0, y0, x1, y1)
        if not screen_rect.colliderect(wrect):
            continue
        drawline(realworld, ColorDoor, camera, (x0, y0), (x1, y1), 5)
        cast_shadow(light, Shadow, camera, player_position, door[0:4])

    for window in area_map["structures"]["windows"]:
        (x0, y0, x1, y1, locked) = window
        wrect = line_to_rect(x0, y0, x1, y1)
        if not screen_rect.colliderect(wrect):
            continue
        drawline(realworld, ColorWindow, camera, (x0, y0), (x1, y1), 5)

    # Draw limits
    draw_limits(realworld, camera)

    # Apply the light to the surface
    realworld.blit(light, (0, 0))

    # TODO: cpu-friendly funky vision updates
    vision = resources["vision"]
    vision.blit(realworld, (0, 0))

    # Adds HUD layer and minimap
    draw_minimap(game_data)
    vision.blit(resources["minimap"], (MinimapMargin, MinimapMargin))

    # Renders the realworld (or the vision, if we got that far with the project)
    screen = pygame.display.get_surface()
    pygame.transform.scale(vision, screen.get_size(), screen)
    pygame.display.flip()

def draw_limits(surface, camera):
    W = mapgenerator.MapWidth * 3
    H = mapgenerator.MapHeight * 3
    EL = -W + mapgenerator.ExitLeft
    ER = mapgenerator.ExitRight
    drawrect(surface, White, camera, (-W, -mapgenerator.MapHeight, W, H))
    drawrect(surface, White, camera, (-mapgenerator.MapWidth, -H, W, H))
    drawrect(surface, White, camera, (mapgenerator.MapWidth, -mapgenerator.MapHeight, W, H))
    drawrect(surface, White, camera, (EL, mapgenerator.MapHeight, W, H))
    drawrect(surface, White, camera, (ER, mapgenerator.MapHeight, W, H))

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
        int(round(float(x) / ScalePosition)),
        int(round(float(y) / ScalePosition))
    )

def get_position(entity):
    return entity["position"]

def set_position(entity, (x, y)):
    entity["position"] = (x, y)

def get_next_position(entity):
    return entity["next_position"]

def set_next_position(entity, (x, y)):
    entity["next_position"] = (x, y)
