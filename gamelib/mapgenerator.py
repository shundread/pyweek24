import pygame
import math
import random

MinimumBuildings = 4
MaximumBuildings = 7
MinimumRooms = 2
MaximumRooms = 4
LotSize = (LotWidth, LotHeight) = (40, 40)
SplitLimit = int(math.ceil(0.4 * LotWidth))
HalfDoorLength = int(math.ceil(0.5 * SplitLimit * 0.3))
DoorLength = HalfDoorLength * 2
HalfWindowLength = HalfDoorLength
WindowLength = HalfWindowLength * 2
WindowChance = 0.3

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
    buildings = {
        "walls": [],
        "doors": [],
        "windows": [],
        "floors": []
    }
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

        buildings["walls"].extend(building["walls"])
        buildings["doors"].extend(building["doors"])
        buildings["windows"].extend(building["windows"])
        buildings["floors"].extend(building["floors"])

    area["buildings"] = buildings

    # Generate open area on the remaining lots
    while len(vacant_lots) > 0:
        lot = vacant_lots.pop()

    game_data["map"] = area

def generate_building(centerx, centery, width, height):
    building = pygame.rect.Rect((centerx, centery), (width, height))
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
                walls.add(wall)

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
            if random.random() < WindowChance:
                segments = add_passage(*wall)
                windows.append(segments["passage"])
                walls.add(segments["walls"][0])
                walls.add(segments["walls"][1])
            else:
                walls.add(wall)

    lwalls = [w for w in walls]
    floors = [make_floor(r) for r in rooms]
    return { "walls": lwalls, "doors": doors, "windows": windows, "floors": floors }

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
    return {
        "passage": (door_x0, door_y0, door_x1, door_y1),
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
