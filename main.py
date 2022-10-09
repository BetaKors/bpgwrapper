from math import sin
from bpgwrapper import *
from player import Player


game = Game()

mouse = Circle(game, game.mouse.pos, 0.1, Color(255, 0, 0), antialiasing=False)
mouse.always_render = True
mouse.layer = 2


def shrink() -> Coroutine:
    initial_radius = mouse.radius

    while True:
        mouse.radius = initial_radius + sin(game.time.frame_count / 10) / 40
        yield None


@game.on_update
def update() -> None:
    mouse.pos = game.mouse.pos


@game.keyboard.on_key_down
def key_down(key: Key) -> None:
    match key:
        case Key.f2:
            game.window.screenshot('screenshot.png', existance_handling='count')
        case Key.f11:
            game.window.toggle_fullscreen()
        case Key.escape:
            game.quit()


game.window.fullscreen = True
game.mouse.visible = False

game.add_component(Player)
game.scheduling.start_coroutine(shrink())

game.mainloop()
