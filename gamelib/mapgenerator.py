import pygame
import math
import random

# Building / Lot dimensions
BuildingSize = 250
LotRows = 5
LotColumns = 5
LotSize = int(BuildingSize * 1.4)

# Limits
MapSize = (MapWidth, MapHeight) = (LotSize * 1.1 * LotColumns, LotSize * 1.1 * LotRows)
ExitLeft = MapWidth * 0.45
ExitRight = MapWidth * 0.55

# Building quantities
MinimumBuildings = 10
MaximumBuildings = 15

# Open area quantities
MinimumTrees = 5
MaximumTrees = 15

# Limit for splitting the buildings
SplitLimit = int(math.ceil(0.4 * BuildingSize))

# Passage dimensions
HalfDoorLength = 20
DoorLength = HalfDoorLength * 2
HalfWindowLength = HalfDoorLength
WindowLength = HalfWindowLength * 2

# Spawn quantities
SpawnsFamily = 3
SpawnsMonsters = 4

# Chances of stuff happening
ChanceWindow = 0.3 # window placement
ChancePassageLock = 0.3 # chance of a door or window being locked

def generate_map(game_data):
    area = {
        "family_spawns": [],
        "monster_spawns": []
    }

    # Generate the lot "vacancies" and shuffle them for assignment of the areas
    vacant_lots = []
    for lotx in range(LotColumns):
        for loty in range(LotRows):
            vacant_lots.append((lotx, loty))
    random.shuffle(vacant_lots)

    # Pick lots at random and generate buildings on them
    n_buildings = random.randint(MinimumBuildings, MaximumBuildings)
    structures = {
        "buildings": [],
        "walls": [],
        "doors": [],
        "windows": [],
        "floors": [],
        "trees": [],
    }
    for b in range(n_buildings):
        # Get the lot's area
        (lotx, loty) = vacant_lots.pop()
        lot = lot_rect(lotx, loty)

        # Sets the building dimensions
        bwidth = int(random.randint(70, 100) * 0.01 * BuildingSize)
        bheight = int(random.randint(70, 100) * 0.01 * BuildingSize)
        bcenterx = lot.centerx
        bcentery = lot.centery
        structure = generate_building(bcenterx, bcentery, bwidth, bheight)

        structures["buildings"].extend(structure["buildings"])
        structures["walls"].extend(structure["walls"])
        structures["doors"].extend(structure["doors"])
        structures["windows"].extend(structure["windows"])
        structures["floors"].extend(structure["floors"])
        if len(area["family_spawns"]) < SpawnsFamily:
            (x, y, w, h, r, g, b) = random.choice(structure["floors"])
            position = (x + int(w * 0.5), y + int(h * 0.5))
            area["family_spawns"].append(position)

    # Generate open areas on the remaining lots
    while len(vacant_lots) > 0:
        # Get the lot's area
        (lotx, loty) = vacant_lots.pop()
        lot = lot_rect(lotx, loty)

        trees = random.randint(MinimumTrees, MaximumTrees)
        for t in range(trees):
            x = random.randint(lot.left, lot.right)
            y = random.randint(lot.top, lot.bottom)

            structures["trees"].append((x, y))

        if len(area["monster_spawns"]) < SpawnsMonsters:
            x = random.randint(lot.left, lot.right)
            y = random.randint(lot.top, lot.bottom)
            area["monster_spawns"].append((x, y))

    area["structures"] = structures

    area["limits"] = [
        (0, 0, 0, MapHeight), #left
        (MapWidth, 0, MapWidth, MapHeight), #right
        (0, 0, MapWidth, 0), #top
        (0, MapHeight, ExitLeft, MapHeight), #bottom-left
        (ExitRight, MapHeight, MapWidth, MapHeight), #bottom-right
        (ExitLeft, MapHeight, ExitLeft, 2*MapHeight), #exit-corridor left
        (ExitRight, MapHeight, ExitRight, 2*MapHeight), #exit-corridor right
    ]

    game_data["map"] = area

def lot_rect(x, y):
    lot = pygame.rect.Rect(0, 0, LotSize, LotSize)
    lot.topleft = (x * LotSize, y * LotSize)
    return lot

def generate_building(centerx, centery, width, height):
    building = pygame.rect.Rect((0, 0), (width, height))
    building.center = (centerx, centery)
    rooms = [building]
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

            next_rooms.extend(split_room(room))
        rooms = next_rooms

    outer_rooms = get_outer_rooms(building, rooms)
    entrance = random.choice(outer_rooms)
    connected_rooms = [entrance]
    disconnected_rooms = [room for room in rooms if room not in connected_rooms]
    doors = []
    walls = set()
    while len(disconnected_rooms) > 0:
        for d in disconnected_rooms:
            for c in connected_rooms:
                wall = shared_wall(d, c)
                if wall is None:
                    continue

                # Works because the wall is aligned along the coordinate axes
                length = (wall[2] - wall[0]) + (wall[3] - wall[1])

                if (d in connected_rooms) or (length < DoorLength):
                    walls.add(wall)
                else:
                    segments = add_passage(*wall)
                    doors.append(segments["passage"])
                    walls.add(segments["walls"][0])
                    walls.add(segments["walls"][1])
                    connected_rooms.append(d)

        disconnected_rooms = [
            r for r in disconnected_rooms if r not in connected_rooms
        ]

    # Connect the rooms to the outside
    windows = []
    n_exits = random.randint(2, max(2, len(outer_rooms) - 2))
    random.shuffle(outer_rooms)
    for room in rooms:
        outer_walls = get_external_walls(building, room)
        if not outer_walls:
            continue
        random.shuffle(outer_walls)

        if n_exits:
            wall = outer_walls.pop()
            segments = add_passage(*wall)
            doors.append(segments["passage"])
            walls.add(segments["walls"][0])
            walls.add(segments["walls"][1])
            n_exits -= 1

        for wall in outer_walls:
            if random.random() < ChanceWindow:
                segments = add_passage(*wall)
                windows.append(segments["passage"])
                walls.add(segments["walls"][0])
                walls.add(segments["walls"][1])
            else:
                walls.add(wall)

    lwalls = [w for w in walls]
    floors = [make_floor(r) for r in rooms]
    rbuilding = [building.left, building.top, building.width, building.height]
    return {
        "buildings": [rbuilding],
        "walls": lwalls,
        "doors": doors,
        "windows": windows,
        "floors": floors
    }

def make_floor(room):
    return (
        room.left, room.top, room.width, room.height,
        random.randint(30, 60), random.randint(30, 60), random.randint(30, 60)
    )

def get_external_walls(building, room):
    walls = []
    if room.left == building.left:
        walls.append((room.left, room.top, room.left, room.bottom))
    if room.right == building.right:
        walls.append((room.right, room.top, room.right, room.bottom))
    if room.top == building.top:
        walls.append((room.left, room.top, room.right, room.top))
    if room.bottom == building.bottom:
        walls.append((room.left, room.bottom, room.right, room.bottom))

    return walls

def shared_wall(room_a, room_b):
    if room_a.left == room_b.right:
        left = right = room_a.left
    if room_a.right == room_b.left:
        left = right = room_a.right
    if room_a.left == room_b.right \
    or room_a.right == room_b.left:
        top = max(room_a.top, room_b.top)
        bottom = min(room_a.bottom, room_b.bottom)
        if bottom > top:
            return (left, top, right, bottom)

    if room_a.top == room_b.bottom:
        top = bottom = room_a.top
    if room_a.bottom == room_b.top:
        top = bottom = room_a.bottom
    if room_a.top == room_b.bottom \
    or room_a.bottom == room_b.top:
        left = max(room_a.left, room_b.left)
        right = min(room_a.right, room_b.right)
        if right > left:
            return (left, top, right, bottom)

    return None

# Result { "passage": passage_coords, "walls": [wall_a_coords, wall_b_coords] }
def add_passage(x0, y0, x1, y1):
    x = int(0.5 * (x0 + x1))
    y = int(0.5 * (y0 + y1))
    dx = int(x0 != x1) * HalfDoorLength
    dy = int(y0 != y1) * HalfDoorLength
    door_x0 = x - dx
    door_x1 = x + dx
    door_y0 = y - dy
    door_y1 = y + dy
    locked = random.random() < ChancePassageLock
    return {
        "passage": (door_x0, door_y0, door_x1, door_y1, locked),
        "walls": (
            (x0, y0, door_x0, door_y0),
            (door_x1, door_y1, x1, y1)
        )
    }

def split_room(room):
    percentage = random.randint(35, 65)
    horizontal = random.random() < (float(room.width) /  float(room.width + room.height))

    if horizontal:
        room_a = pygame.rect.Rect(
            room.topleft,
            (int(room.width * percentage * 0.01), room.height))
        room_b = pygame.rect.Rect(
            room_a.topright,
            (room.width - room_a.width, room.height))
    else:
        room_a = pygame.rect.Rect(
            room.topleft,
            (room.width, int(room.height * percentage * 0.01)))
        room_b = pygame.rect.Rect(
            room_a.bottomleft,
            (room.width, room.height - room_a.height))
    return [room_a, room_b]

def get_outer_rooms(building, rooms):
    result = []
    for room in rooms:
        if room.left == building.left \
        or room.right == building.right \
        or room.top == building.top \
        or room.bottom == building.bottom:
            result.append(room)

    return result
