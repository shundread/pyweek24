'''A swappable module for the game's engine.'''

import pygame
import titlescreen

def init():
    try:
        pygame.init()
        pygame.display.set_mode((600, 600))
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([
            pygame.QUIT,
            pygame.KEYDOWN,
        ])
        titlescreen.init()
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
    gamestate = data["gamestate"]
    if (gamestate == "title"):
        return titlescreen.handle_key(game, data["title"], event)
    if (gamestate == "newgame"):
        data["gamestate"] = "newtitle"

def simulate(game, data, dt):
    gamestate = data["gamestate"]
    if (gamestate == "newtitle"):
        data["title"] = titlescreen.reset_data()
        data["gamestate"] = "title"
    if (gamestate == "title"):
        return titlescreen.simulate(game, data["title"], dt)

def render(data):
    if (data["gamestate"] == "title"):
        return titlescreen.render(data["title"])

def handle_swap(game, data):
    try:
        print("Attempting to swap titlescreen")
        reload(titlescreen)
        titlescreen.handle_swap(game)
        print("titlescreen swapped\n")
    except Exception as error:
        print("Unable to swap the titlescreen, reason:")
        print(error)
        return

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
