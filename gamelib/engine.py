'''A swappable module for the game's engine.'''

import pygame

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
        if event.type == pygame.KEYDOWN: return handle_key(game, data, event)

def handle_key(game, data, event):
    if event.key == pygame.K_F5: return game.request_swap()
    print("Key pressed:", event)

def render(data):
    pass
