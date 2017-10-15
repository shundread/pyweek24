'''A swappable module for the game's engine.'''

import pygame
import titlescreen

def init():
    try:
        pygame.init()
        pygame.display.set_mode((400, 400))
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([
            pygame.QUIT,
            pygame.KEYDOWN,
        ])
    except Exception as error:
        print("Unable to (re) initialize the module, reason:\n{0}".format(error))


def handle_input(game, data):
    for event in pygame.event.get():
        ########################################
        # Handle some very special cases first #
        ########################################

        # Always let the user quit
        if event.type == pygame.QUIT:
            return game.quit()

        # Swap handling and data dump / reload
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1: return handle_swap(game, data)
            if event.key == pygame.K_F5: return game.dump_data()
            if event.key == pygame.K_F9: return game.load_data()

        # Check if we're in different gamestates and delegate input handle to
        if event.type == pygame.KEYDOWN:
            return handle_key(game, data, event)

        # If we got this far then we got no idea what we're handling with
        print("Unrecognized event: {0}".format(event))

def handle_key(game, data, event):
    if (data["gamestate"] == "title"):
        return titlescreen.handle_key(game, data, event)

    print("Key pressed:", event)

def simulate(game, data, dt):
    if (data["gamestate"] == "title"):
        return titlescreen.simulate(game, data, dt)

def render(data):
    if (data["gamestate"] == "title"): return titlescreen.render(data)

def handle_swap(game, data):
    try:
        print("Attempting to swap titlescreen")
        reload(titlescreen)
        print("titlescreen swapped\n")
    except Exception as error:
        print("Unable to swap the titlescreen, reason:")
        print(error)

    upgrade_data(data)
    game.request_swap()

def upgrade_data(data):
    try:
        print("Upgrading the game data. Old data:")
        print(data)
        if "gamestate" not in data:
            data["gamestate"] = "title"
        print("\nThe new data:")
        print(data)
        print("")
    except Exception as error:
        print("Unable to upgrade the data, reason: {0}".format(error))
