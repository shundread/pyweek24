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

MinimumBuildings = 10
MaximumBuildings = 20
MinimumRooms = 2
MaximumRooms = 4
LotSize = (LotWidth, LotHeight) = (100, 100)
def generate_map(game_data):
    area = {}

    # Generate the lot "vacancies" and shuffle them for assignment of the areas
    vacant_lots = []
    for lotx in [-2, -1, 0, 1, 2]:
        for loty in [-2, -1, 0, 1, 2]:
            vacant_lots.append((lotx, loty))
    random.shuffle(vacant_lots)

    # Pick lots at random and generate buildings on them
    n_buildings = random.randint(MinimumBuildings, MaximumBuildings)
    buildings = []
    for b in range(n_buildings):
        # Get the lot's X, Y index
        (lotx, loty) = vacant_lots.pop()
        # TODO store polygons

        # Scale the lot's coordinates
        lot = pygame.rect.Rect(0, 0, LotWidth, LotHeight)
        lot.center = (lotx * LotWidth, loty * LotHeight)

        # Set the corridor size to cover ~50/70% of the lot
        cwidth = int(random.randint(55, 85) * 0.01 * LotWidth)
        cheight = int(random.randint(55, 85) * 0.01 * LotHeight)
        ccenterx = lot.centerx + int(random.randint(-10, 10) * 0.01 * LotWidth)
        ccentery = lot.centery + int(random.randint(-10, 10) * 0.01 * LotHeight)
        building = generate_building(ccenterx, ccentery, cwidth, cheight)

        buildings.extend(building)

    area["buildings"] = buildings

    # Generate open area on the remaining lots
    while len(vacant_lots) > 0:
        lot = vacant_lots.pop()

    game_data["map"] = area

SplitLimit = int(0.3 * LotWidth) # Stop splitting rooms at this size
def generate_building(centerx, centery, width, height):
    rooms = [pygame.rect.Rect((centerx, centery), (width, height))]
    splitting = True
    while splitting:
        splitting = False
        next_rooms = []
        for room in rooms:
            if room.width < SplitLimit \
            or room.height < SplitLimit:
                next_rooms.append(room)
                continue

            splitting = True
            percentage = random.randint(35, 65)
            horizontal = random.random() < (float(room.width) /  float(room.width + room.height))
            if horizontal:
                room_a = pygame.rect.Rect(room.topleft, (int(room.width * percentage * 0.01), room.height))
                room_b = pygame.rect.Rect(room_a.topright, (room.width - room_a.width, room.height))
                next_rooms.extend([room_a, room_b])
            else:
                room_a = pygame.rect.Rect(room.topleft, (room.width, int(room.height * percentage * 0.01)))
                room_b = pygame.rect.Rect(room_a.bottomleft, (room.width, room.height - room_a.height))
                next_rooms.extend([room_a, room_b])
        rooms = next_rooms

    print("Rooms is {0}".format(rooms))
    return rooms

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
        pygame.draw.rect(realworld, White, (x - px, y - py, w, h), 1)

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
