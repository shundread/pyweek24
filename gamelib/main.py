'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import data
import engine
import pygame

class Game(object):
    '''A class that delegates its engine functionalities to a hot-swappable
    module'''
    FPS = 60.0

    def __init__(self):
        self.running = False
        self.data = {}

    def run(self):
        engine.init()

        clock = pygame.time.Clock()
        self.running = True
        while self.running:
            engine.handle_input(self, self.data)
            engine.render(self.data)
            clock.tick(self.FPS)

    def quit(self):
        self.running = False

    def request_swap(self):
        print("Attempting to swap the engine")
        try:
            print("Swapping the module")
            reload(engine)
            print("Reinitializing the module")
            engine.init()
        except Exception as error:
            print("Unable to swap the engine, reason:\n{0}".format(error))
        print("Engine swapped")

def main():
    game = Game()
    game.run()
