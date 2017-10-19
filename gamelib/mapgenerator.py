import pygame
import math
import random

MinimumBuildings = 10
MaximumBuildings = 20
MinimumRooms = 2
MaximumRooms = 4
LotSize = (LotWidth, LotHeight) = (80, 80)
SplitLimit = int(math.ceil(0.4 * LotWidth))
HalfDoorLength = int(math.ceil(0.5 * SplitLimit * 0.3))
DoorLength = HalfDoorLength * 2
HalfWindowLength = HalfDoorLength
WindowLength = HalfWindowLength * 2


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

    external_rooms = get_external_rooms(building, rooms)
    entrance = random.choice(external_rooms)
    connected_rooms = [entrance]
    disconnected_rooms = [room for room in rooms if room not in connected_rooms]
    doors = []
    connections = {}
    while len(disconnected_rooms) > 0:
        for d in disconnected_rooms:
            for c in connected_rooms:
                if d.left == c.right or d.right == c.left:
                    top = max(d.top, c.top)
                    bottom = min(d.bottom, c.bottom)
                    if bottom - top < DoorLength:
                        continue
                    centery = int((bottom + top) * 0.5)
                    y0 = centery - HalfDoorLength
                    y1 = centery + HalfDoorLength
                    if d.left == c.right:
                        x = d.left
                    else:
                        x = d.right
                    doors.append([x, y0, x, y1])
                    connected_rooms.append(d)
                    break
                if d.top == c.bottom or d.bottom == c.top:
                    left = max(d.left, c.left)
                    right = min(d.right, c.right)
                    if right - left < DoorLength:
                        continue
                    centerx = int((right + left) * 0.5)
                    x0 = centerx - HalfDoorLength
                    x1 = centerx + HalfDoorLength
                    if d.top == c.bottom:
                        y = d.top
                    else:
                        y = d.bottom
                    doors.append([x0, y, x1, y])
                    connected_rooms.append(d)
                    break

            if d in connected_rooms:
                break
        disconnected_rooms = [
            r for r in disconnected_rooms if r not in connected_rooms
        ]

    # Connect the rooms to the outside
    n_exits = random.randint(2, max(2, len(external_rooms) - 2))
    exit_rooms = random.sample(external_rooms, n_exits)
    for r in exit_rooms:
        candidates = []
        if r.left == building.left: candidates.append("l")
        if r.right == building.right: candidates.append("r")
        if r.top == building.top: candidates.append("t")
        if r.bottom == building.bottom: candidates.append("b")

        exit = random.choice(candidates)
        if exit in "lr":
            if exit == "l":
                x = r.left
            else:
                x = r.right
            y0 = r.centery - HalfDoorLength
            y1 = r.centery + HalfDoorLength
            doors.append([x, y0, x, y1])
        else:
            if exit == "t":
                y = r.top
            else:
                y = r.bottom
            x0 = r.centerx - HalfDoorLength
            x1 = r.centerx + HalfDoorLength
            doors.append([x0, y, x1, y])

    return { "walls": rooms, "doors": doors, "windows": [], "floors": [] }

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

def get_external_rooms(building, rooms):
    result = []
    for room in rooms:
        if room.left == building.left \
        or room.right == building.right \
        or room.top == building.top \
        or room.bottom == building.bottom:
            result.append(room)

    return result
