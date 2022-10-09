from bpgwrapper import *


class Player(Component):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self.pos = Vector2()

        self.circle = Circle(self._game, Vector2(), 1, Color('#2B59C3'))
        self.circle.always_render = True
        self.circle.pos = self.pos
        self.circle.layer = 1

    @property
    def movement(self) -> Vector2:
        movement = Vector2(
            self._game.keyboard.get_axis(Key.a, Key.d),
            self._game.keyboard.get_axis(Key.s, Key.w),
        )

        return normalize_vec2_if_possible(movement) * self.speed * self._game.time.deltatime

    @property
    def speed(self) -> float:
        return 8 if self._game.keyboard.get_key_pressed(Key.left_shift) else 4

    def update(self) -> None:
        self.pos += self.movement
        self._game.camera.pos = self._calculate_new_camera_position()

    def _calculate_new_camera_position(self) -> Vector3:
        target = Vector3(*self.pos, self._game.camera.pos.z)  # type: ignore
        return self._game.camera.pos.lerp(target, clamp(self._game.time.deltatime * 7, 0, 1))
