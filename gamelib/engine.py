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
        if event.type == pygame.QUIT: return game.quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
            return swap(game, data)
        if event.type == pygame.KEYDOWN: return handle_key(game, data, event)

def handle_key(game, data, event):
    if event.key == pygame.K_F5: return swap(game, data)
    print("Key pressed:", event)

def simulate(game, data, dt):
    pass

def render(data):
    if (data["gamestate"] == "title"): return titlescreen.render(data)

def swap(game, data):
    try:
        print("Attempting to swap titlescreen")
        reload(titlescreen)
        print("titlescreen swapped")
        print("")
    except Exception as error:
        print("Unable to swap the titlescreen, reason: {0}".format(error))

    upgrade_data(data)
    game.request_swap()

def upgrade_data(data):
    try:
        print("Upgrading the game data")
        print("Old data:")
        print(data)
        print("")
        if "gamestate" not in data:
            data["gamestate"] = "title"
        print("The new data:")
        print(data)
        print("")
    except Exception as error:
        print("Unable to upgrade the data, reason: {0}".format(error))
