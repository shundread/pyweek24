'''A swappable module for the game's engine.'''

import pygame
import titlescreen
import play
import intro
import ending

def init():
    try:
        pygame.init()
        pygame.display.set_mode((600, 600))
        pygame.display.get_surface().fill((0, 0, 0))
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([
            pygame.QUIT,
            pygame.KEYDOWN,
            pygame.MOUSEMOTION
        ])
        titlescreen.init()
    except Exception as error:
        print("Unable to (re) initialize the module, reason:\n{0}".format(error))
        raise error


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
        if event.type == pygame.MOUSEMOTION:
            return
        print("Unrecognized event: {0}".format(event))

def handle_key(game, data, event):
    gamestate = data["gamestate"]
    if (gamestate == "title"):
        return titlescreen.handle_key(game, data["title"], event)
    if (gamestate == "intro"):
        return intro.handle_key(game, data["intro"], event)
    if (gamestate == "game"):
        return play.handle_key(game, data["game"], event)

def simulate(game, data, dt):
    gamestate = data["gamestate"]

    # Title #
    if gamestate == "newtitle":
        data["title"] = titlescreen.reset_data()
        titlescreen.init()
        data["gamestate"] = "title"
    if gamestate == "title":
        return titlescreen.simulate(game, data["title"], dt)

    # Intro #
    if gamestate == "newintro":
        data["intro"] = intro.reset_data()
        intro.init()
        data["gamestate"] = "intro"
    if gamestate == "intro":
        return intro.simulate(game, data["intro"], dt)

    # New game #
    if gamestate == "newgame":
        data["game"] = play.reset_data()
        play.init()
        play.generate_map(data["game"])
        data["gamestate"] = "game"
    if gamestate == "game":
        return play.simulate(game, data["game"], dt)

    # Ending #
    if gamestate == "newending":
        data["ending"] = ending.reset_data()
        ending.init()
        ending.set_text(ending.EndingTexts[data["survivors"]])
        data["gamestate"] = "ending"
    if gamestate == "ending":
        return ending.simulate(game, data["ending"], dt)

def render(data):
    gamestate = data["gamestate"]
    if gamestate == "title":
        return titlescreen.render(data["title"])
    if gamestate == "intro":
        return intro.render(data["intro"])
    if gamestate == "game":
        return play.render(data["game"])
    if gamestate == "ending":
        return ending.render(data["ending"])

def handle_swap(game, data):
    try:
        print("Attempting to swap titlescreen module")
        reload(titlescreen)
        titlescreen.handle_swap(game)
        print("titlescreen swapped\n")

        print("Attempting to swap intro module")
        reload(intro)
        intro.handle_swap(game)
        print("Swapped intro module")

        print("Attempting to swap play module")
        reload(play)
        play.handle_swap(game)
        print("Play module swapped")

        print("Attempting to swap ending module")
        reload(ending)
        ending.handle_swap(game)
        print("Swapped ending module")

    except Exception as error:
        print("Unable to swap the submodules, reason:")
        print(error)
        raise error

    upgrade_data(data)
    game.request_swap()

def upgrade_data(data):
    try:
        print("Upgrading the game data. Old data:")
        print(data)
        if "gamestate" not in data:
            data["gamestate"] = "newtitle"
        print("\nThe new data:")
        print(data)
        print("")
    except Exception as error:
        print("Unable to upgrade the data, reason: {0}".format(error))
        raise error
