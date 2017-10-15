import pygame
import tween

def handle_key(game, data, event):
    print("Titlescreen: key pressed {0}".format(event))

def simulate(game, data, dt):
    data["miliseconds"] += dt

    miliseconds = data["miliseconds"]
    # 0-1000 ms: Fade in
    if miliseconds < 2000:
        brightness = int(tween.sin(0, 255, miliseconds/2000.0))
        data["background_color"] = (brightness, brightness, brightness)
    else:
        data["background_color"] = (255, 255, 255)

def render(data):
    pygame.display.get_surface().fill(data["background_color"])
    pygame.display.flip()

def reset_data():
    return {
        "miliseconds": 0,
        "background_color": (0, 0, 0),
    }

def handle_swap(game):
    reload(tween)
    game.data["title"] = reset_data()
