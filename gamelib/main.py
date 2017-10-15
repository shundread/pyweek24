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

        # Swapping state
        self.swapped = False

        # Error states
        self.input_handle_error = None
        self.simulate_error = None
        self.render_error = None

    def run(self):
        engine.init()

        clock = pygame.time.Clock()
        self.running = True
        dt = 0
        while self.running:
            self.handle_input()
            if self.swapped:
                self.swapped = False
                continue
            self.simulate(dt)
            self.render()
            clock.tick(self.FPS)

    def handle_input(self):
        try:
            engine.handle_input(self, self.data)
            self.input_handling_error = None
        except Exception as error:
            if self.input_handling_error != error.message:
                print("Unable to handle input, reason:")
                print(error)
                self.input_handling_error = error.message

    def simulate(self, dt):
        try:
            engine.simulate(self, self.data, dt)
            self.simulate_error = None
        except Exception as error:
            if self.simulate_error != error.message:
                print("Unable to render, reason: {0}".format(error.message))
                self.simulate_error = error.message

    def render(self):
        try:
            engine.render(self.data)
            self.render_error = None
        except Exception as error:
            if self.render_error != error.message:
                print("Unable to render, reason:")
                print(error)
                self.render_error = error.message

    def quit(self):
        self.running = False

    def request_swap(self):
        try:
            print("Attempting to swap engine...")
            reload(engine)
            print("Engine swapped. Reinitializing engine...")
            engine.init()
            print("Engine reinitialized")
            print("")
        except Exception as error:
            print("Errors were thrown in the engine swap:\n{0}".format(error))

def main():
    game = Game()
    game.run()
