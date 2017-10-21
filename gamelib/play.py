import pygame
import numpy
import math
import random

import data
import mapgenerator

# Colors
Black = (0, 0, 0)
White = (255, 255, 255)
ColorDoor = (140, 110, 0)
ColorWall = (128, 128, 128)
ColorWindow = (0, 0, 255)
ColorTree = (130, 110, 0)

ColorHead = (200, 200, 0)
ColorShirt = (30, 200, 40)
ColorDeadHead = (130, 100, 100)
ColorDeadShirt = (60, 40, 40)

ColorMonster = (170, 0, 40)
ColorMonsterParticle = (250, 35, 80)

ColorSchemeAlive = (ColorHead, ColorShirt)
ColorSchemeDead = (ColorDeadHead, ColorDeadShirt)

ColorSound = (255, 0, 0)

# Surface info
Size = (Width, Height) = (200, 200)

# Minimap info
MinimapSize = (MinimapWidth, MinimapHeight) = (int(Width * 0.15), int(Height * 0.15))
MinimapMargin = (int(MinimapWidth * 0.5), int (MinimapHeight * 0.5))
MinimapAlpha = 255
MinimapForeground = (160, 240, 80)
MinimapBackground = (60, 100, 150)
MinimapPersonIndicator = (20, 0, 20)

# Light parameters
HalfConeAngle = 0.20 * math.pi
Shadow = White
ShadowAlpha = 255
ShadowLength = Width * 20

# Hud parameters
HudAlpha = 255

# Funky update parameters (UNUSED)
Pass = 0.40

# Entity size info
SizeHead = 4
SizeShoulder = 4
SizeTorso = 5

SizeMonsterBlob = 6
SizeTree = 8

ScalePosition = 20

# Collision box sizes
BoxPerson = 12 * ScalePosition
BoxMonster = 15 * ScalePosition

# Distances
DistanceRescue = 30 * ScalePosition
DistanceFollow = 28 * ScalePosition
DistanceInteract = 20 * ScalePosition

# Speeds
SpeedPerson = 2
SpeedMonster = 2 * SpeedPerson

# Monster timers
TimerRest = 8000
TimerHunt = 4000
TimerWander = 4000
TimerDeath = 2000
TimerUncertainty = 1000

# Sound info
StepSoundThreshold = 300

SoundStepDistance = 1500
SoundOpenDistance = 2500
SoundNotOpenDistance = 2500
SoundBreakDistance = 8000

# SoundMonsterStepDistance = 3000 we just add 1500 elsewhere
SoundMonsterVoiceDistance = 8000

def reset_data():
    return {
        "miliseconds": 0,
        "player": {
            "type": "human",
            "position": (0, 0),
            "next_position": (0, 0),
            "state": "alive",
            "stepsound": 0,
        },
        "characters": [],
        "sounds": [],
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
    if ShadowAlpha < 255:
        resources["light"].set_alpha(ShadowAlpha)

    resources["hud"] = pygame.surface.Surface(Size)
    resources["hud"].convert()
    resources["hud"].set_colorkey(Black)
    if HudAlpha < 255:
        resources["hud"].set_alpha(HudAlpha)

    resources["vision"] = pygame.surface.Surface(Size)
    pygame.transform.scale(screen, Size, resources["vision"])

    ###############
    # Load audios #
    ###############
    resources["human_step_0"] = pygame.mixer.Sound(data.filepath("human_step_0.wav"))
    resources["human_step_1"] = pygame.mixer.Sound(data.filepath("human_step_0.wav"))
    resources["monster_step_0"] = pygame.mixer.Sound(data.filepath("monster_step_0.wav"))
    resources["monster_step_1"] = pygame.mixer.Sound(data.filepath("monster_step_1.wav"))
    resources["break_door"] = pygame.mixer.Sound(data.filepath("break_door.wav"))
    resources["break_window"] = pygame.mixer.Sound(data.filepath("break_window.wav"))
    resources["open_door"] = pygame.mixer.Sound(data.filepath("open_door.wav"))
    resources["open_window"] = pygame.mixer.Sound(data.filepath("open_window.wav"))
    resources["open_not"] = pygame.mixer.Sound(data.filepath("open_not.wav"))
    resources["kill"] = pygame.mixer.Sound(data.filepath("kill.wav"))
    resources["growl"] = pygame.mixer.Sound(data.filepath("growl.wav"))
    resources["chase"] = pygame.mixer.Sound(data.filepath("chase.wav"))

    # Initiate tense music
    resources["music"] = pygame.mixer.music.load(data.filepath("ambience1_normal.mp3"))
    pygame.mixer.music.play(-1)


def generate_map(game_data):
    mapgenerator.generate_map(game_data)

    # Place the player & other family members
    family_spawns = game_data["map"]["family_spawns"]
    (x, y) = family_spawns.pop()
    set_position(game_data["player"], (x * ScalePosition, y * ScalePosition))

    game_data["characters"] = []
    for (n, (x, y)) in enumerate(game_data["map"]["family_spawns"]):
        game_data["characters"].append({
            "type": "human",
            "position": (x * ScalePosition, y * ScalePosition),
            "next_position": (x * ScalePosition, y * ScalePosition),
            "angle": n,
            "state": "hiding",
            "stepsound": 0,
        })

    # Place the monsters
    game_data["monsters"] = []
    for (n, (x, y)) in enumerate(game_data["map"]["monster_spawns"]):
        game_data["monsters"].append({
            "type": "monster",
            "position": (x * ScalePosition, y * ScalePosition),
            "next_position": (x * ScalePosition, y * ScalePosition),
            "target_location": (x * ScalePosition, y * ScalePosition),
            "angle": n,
            "state": "rest",
            "timer": TimerRest + random.randint(-TimerUncertainty, TimerUncertainty),
            "stepsound": 0,
        })


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
    location = get_position(game_data["player"])
    if open_passage(game_data, doors, force=False):
        playsound(game_data, "open_door", location, SoundOpenDistance, True)
    elif open_passage(game_data, windows, force=False):
        playsound(game_data, "open_window", location, SoundOpenDistance, True)
    else:
        playsound(game_data, "open_not", location, SoundNotOpenDistance, True)

def force_open(game_data):
    structures = game_data["map"]["structures"]
    doors = structures["doors"]
    windows = structures["windows"]
    location = get_position(game_data["player"])
    if open_passage(game_data, doors, force=True):
        playsound(game_data, "break_door", location, SoundBreakDistance, True)
    elif open_passage(game_data, windows, force=True):
        playsound(game_data, "break_window", location, SoundBreakDistance, True)

def open_passage(game_data, passages, force):
    player_position = get_position(game_data["player"])
    for (i, item) in enumerate(passages):
        (x0, y0, x1, y1, locked) = item
        (x, y) = (0.5 * ScalePosition * (x0 + x1), 0.5 * ScalePosition * (y0 + y1))
        distance = point_point_distance(player_position, (x, y))
        if distance < DistanceInteract:
            if force:
                passages.pop(i)
                return True

            if locked:
                return False
            else:
                passages.pop(i)
                return True

def simulate(game, game_data, dt):
    game_data["miliseconds"] += dt

    # Update / clear sounds
    sounds = game_data["sounds"]
    for sound in sounds:
        sound["timer"] -= dt * 5
    game_data["sounds"] = [sound for sound in sounds if sound["timer"] > 0]

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
    for c0 in characters:
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

    # Update monsters
    monsters = game_data["monsters"]
    for m in monsters:
        # Discount timers and possibly change the monster's state
        m["timer"] -= dt
        if m["timer"] < 0:
            next_state = random.choice(("rest", "wander"))
            if next_state == "rest":
                set_monster_state(m, "rest", TimerRest)
                m["target_location"] = get_position(m)
                playsound(game_data, "growl", get_position(m), SoundMonsterVoiceDistance, False)
            else:
                set_monster_state(m, "wander", TimerWander)
                x = random.randint(0, int(mapgenerator.MapWidth * ScalePosition))
                y = random.randint(0, int(mapgenerator.MapHeight * ScalePosition))
                m["target_location"] = (x,  y)

        # Walk towards the location
        (x, y) = pm = get_next_position(m)
        (tx, ty) = m["target_location"]
        (xd, yd) = (tx - x, ty - y)
        if xd or yd:
            if m["state"] == "wander":
                speed = SpeedPerson
            else:
                speed = SpeedMonster
            angle = math.atan2(yd, xd)
            nx = x + min(math.cos(angle) * speed * dt, xd)
            ny = y + min(math.sin(angle) * speed * dt, yd)
            set_next_position(m, (nx, ny))

        # Kill characters
        for c in all_characters:
            (xc, yc) = pc = get_next_position(c)
            distance = point_point_distance(pc, pm)
            if distance < BoxMonster:
                kill_character(game_data, c)

    # The player never gets pushed around, only killed :)
    (dx, dy) = (0, 0)
    if keys[pygame.K_w]: dy -= SpeedPerson * dt
    if keys[pygame.K_s]: dy += SpeedPerson * dt
    if keys[pygame.K_a]: dx -= SpeedPerson * dt
    if keys[pygame.K_d]: dx += SpeedPerson * dt
    set_next_position(player, (px + dx, py + dy))

    # Bleeds dying characters to death
    all_characters = characters + [player]
    for character in all_characters:
        if character["state"] in ["dead", "dying"]:
            timer = character["deathtimer"]
            character["deathtimer"] = max(timer - dt, 0)
            if character["deathtimer"] == 0:
                character["state"] = "dead"

            # Prevent dead or dying characters from moving
            set_next_position(character, get_position(character))

    # Collide characters with solid structures
    area_map = game_data["map"]
    structures = area_map["structures"]

    # Collide characters with trees
    for c in all_characters + monsters:
        for tree in structures["trees"]:
            (xc, yc) = pc = get_next_position(c)
            (xt, yt) = pt = (tree[0] * ScalePosition, tree[1] * ScalePosition)

            distance = point_point_distance(pt, pc)
            if distance < SizeTree * ScalePosition:
                (dx, dy) = (xt - xc, yt - yc)
                angle = math.atan2(dy, dx)
                pushback = SizeTree * ScalePosition

                nx = xc - math.cos(angle) * pushback
                ny = yc - math.sin(angle) * pushback
                set_next_position(c, (nx, ny))

    # Collide characters with walls

    line_barriers = \
        structures["windows"] + \
        structures["doors"] + \
        structures["walls"] + \
        area_map["limits"]

    barrier_rects = []
    for unscaled_line in line_barriers:
        scaled_line = [v * ScalePosition for v in unscaled_line[0:4]]
        barrier_rects.append(line_to_rect(*scaled_line))

    for character in all_characters + monsters:
        if character["type"] == "human":
            box = BoxPerson
        else:
            box = BoxMonster
        (x, y) = get_position(character)
        (x1, y1) = get_next_position(character)
        (dx, dy) = (x1 - x, y1 - y)
        rect0 = pygame.rect.Rect(0, 0, box, box)
        rect0.center = (x, y)

        for lrect in barrier_rects:
            # Collide horizontal
            if dx:
                xrect = pygame.rect.Rect(0, 0, box, box)
                xrect.center = (x + dx, y)
                crect = rect0.union(xrect)
                collision = rects_collision(crect, lrect)
                if collision[0]:
                    if dx > 0:
                        crect.right = lrect.left
                    else:
                        crect.left = lrect.right

                    dx = crect.centerx - x

            # Collide vertical
            if dy:
                yrect = pygame.rect.Rect(0, 0, box, box)
                yrect.center = (x, y + dy)
                crect = rect0.union(yrect)
                collision = rects_collision(crect, lrect)
                if collision[1]:
                    if dy > 0:
                        crect.bottom = lrect.top
                    else:
                        crect.top = lrect.bottom
                    dy = crect.centery - y

        set_position(character, (x + dx, y + dy))
        set_next_position(character, (x + dx, y + dy))

        # Make stepping sounds
        if dx or dy:
            character["stepsound"] += dt
        else:
            character["stepsound"] = max(0, character["stepsound"] - dt * 0.3)
        if character["stepsound"] > StepSoundThreshold:
            emit_step_sound(game_data, character)

def check_game_over(game, game_data):
    player = game_data["player"]
    if player["state"] == "dead":
        game.data["gamestate"] = "newending"
        game.data["survivors"] = 0
        return True

    (x, y) = get_render_position(player)
    if y > mapgenerator.MapHeight + 100:
        game.data["gamestate"] = "newending"
        game.data["survivors"] = count_survivors(game_data)
        return True

def count_survivors(game_data):
    if game_data["player"]["state"] == "dead":
        return 0
    survivors = 1
    for character in game_data["characters"]:
        if character["state"] == "following":
            survivors += 1
    return survivors

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
    player = game_data["player"]
    player_position = (px, py) = get_render_position(player)
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
    # light.fill(White)
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
        if character["state"] in ["dead", "dying"]:
            (head, shirt) = ColorSchemeDead
        else:
            (head, shirt) = ColorSchemeAlive
        drawcharacter(realworld, head, shirt, camera, position, angle)

    # TODO draw the monsters
    for monster in game_data["monsters"]:
        position = get_render_position(monster)
        angle = monster["angle"]
        drawmonster(realworld, camera, position, game_data["miliseconds"])

    # Draw the player
    if player["state"] in ["dead", "dying"]:
        (head, shirt) = ColorSchemeDead
    else:
        (head, shirt) = ColorSchemeAlive
    drawcharacter(realworld, head, shirt, camera, position, angle)

    drawcharacter(realworld, head, shirt, camera, player_position, mouse_angle)

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

    for tree in area_map["structures"]["trees"]:
        wrect = pygame.rect.Rect(0, 0, 2 * SizeTree, 2 * SizeTree)
        wrect.center = tree
        if not screen_rect.colliderect(wrect):
            continue
        (x, y) = tree
        (dx, dy) = (x - px, y - py)
        angle = math.atan2(dy, dx) + math.pi * 0.5
        drawcircle(realworld, ColorTree, camera, tree, SizeTree)
        x0 = x - math.cos(angle) * SizeTree
        y0 = y - math.sin(angle) * SizeTree
        x1 = x + math.cos(angle) * SizeTree
        y1 = y + math.sin(angle) * SizeTree
        cast_shadow(light, Shadow, camera, player_position, (x0, y0, x1, y1))

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
    hud = resources["hud"]
    hud.fill(Black)
    for sound in game_data["sounds"]:
        draw_sound(hud, sound, camera)
    vision.blit(hud, (0, 0))

    screen = pygame.display.get_surface()
    pygame.transform.scale(vision, screen.get_size(), screen)
    pygame.display.flip()

def draw_sound(surface, sound, camera):
    size = max(1, int((sound["distance"] - sound["timer"]) / ScalePosition))
    drawcircle(surface, ColorSound, camera, get_render_position(sound), size, 1)

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

def drawcircle(surface, color, (cx, cy), (x, y), radius, width=0):
    pygame.draw.circle(surface, color, (x - cx, y - cy), radius, width)

def drawrect(surface, color, (cx, cy), (x, y, w, h)):
    pygame.draw.rect(surface, color, ((x - cx, y - cy), (w, h)))

def drawline(surface, color, (cx, cy), (x0, y0), (x1, y1), width):
    pygame.draw.line(surface, color, (x0 - cx, y0 - cy), (x1 - cx, y1 - cy), width)

def drawpoly(surface, color, (cx, cy), points):
    transposed = [(x - cx, y - cy) for (x, y) in points]
    pygame.draw.polygon(surface, color, transposed)

def drawpixel(surface, color, (cx, cy), (px, py)):
    surface.set_at((px - cx, py - cy), color)

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
    drawcircle(surface, color_shirt, camera, shoulder_left, SizeShoulder)
    drawcircle(surface, color_shirt, camera, shoulder_right, SizeShoulder)
    drawcircle(surface, color_shirt, camera, position, SizeTorso)
    drawcircle(surface, color_head, camera, position, SizeHead)

def drawmonster(surface, camera, (x, y), miliseconds):
    t = miliseconds / 1000.0
    for i in range(5):
        angle = (i * (t + i) * math.pi / 5)
        (dx, dy) = (int(math.cos(angle) * 5), int(math.sin(angle) * 5))
        drawcircle(surface, ColorMonster, camera, (x + dx, y + dy), SizeMonsterBlob)
    for p in range(20):
        angle = random.random() * 2 * math.pi
        distance = random.randint(0, 8)
        (dx, dy) = (int(math.cos(angle) * distance), int(math.sin(angle) * distance))
        drawpixel(surface, ColorMonsterParticle, camera, (x + dx, y + dy))

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

def kill_character(game_data, character):
    if character["state"] in ["dead", "dying"]:
        return
    playsound(game_data, "kill", get_position(character), SoundMonsterVoiceDistance, False)
    character["state"] = "dying"
    character["deathtimer"] = TimerDeath

def emit_step_sound(game_data, character):
    character["stepsound"] = 0
    soundname = "{0}_step_{1}".format(character["type"], random.randint(0, 1))
    location = get_position(character)
    if character["type"] == "human":
        is_tasty = True
        distance = SoundStepDistance
    else:
        is_tasty = False
        distance = SoundStepDistance * 2
    playsound(game_data, soundname, location, distance, is_tasty)

def playsound(game_data, soundname, location, hearing_distance, alert_monsters):
    # TODO check if player is too far to hear the sound
    game_data["sounds"].append({
            "timestamp": game_data["miliseconds"],
            "position": location,
            "distance": hearing_distance,
            "timer": hearing_distance,
    })

    if alert_monsters:
        for monster in game_data["monsters"]:
            mpos = get_position(monster)
            mdist = point_point_distance(location, mpos)
            if mdist < hearing_distance:
                if monster["state"] != "hunt":
                    playsound(game_data, "chase", mpos, SoundMonsterVoiceDistance, False)
                set_monster_state(monster, "hunt", TimerHunt)
                monster["target_location"] = location

    # TODO alert monsters about tasty stuff
    resources[soundname].play()

def set_monster_state(monster, state, timer):
    monster["state"] = state
    monster["timer"] = timer + random.randint(-TimerUncertainty, TimerUncertainty)
