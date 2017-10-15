import pygame

def handle_key(game, data, event):
    print("Titlescreen: key pressed {0}".format(event))

def simulate(game, data, dt):
    title = data["title"]:
    title["frame"] += dt

def render(data):
    pygame.display.get_surface().fill((0, 0, 255))
    pygame.display.flip()
