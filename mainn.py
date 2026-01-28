from arcade.examples.radar_sweep import CENTER_X, CENTER_Y
from pyglet.graphics import Batch
import arcade
import math
import enum
import random

SCREEN_WIDTH = arcade.get_display_size()[0]
SCREEN_HEIGHT = arcade.get_display_size()[1]
SCREEN_TITLE = "Спрайтовый герой"
TILE_SCALING = 2


class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1


class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Основные характеристики
        self.scale = TILE_SCALING * 0.25
        self.speed = 4
        self.health = 100

        # Загрузка текстур
        self.idle_texture = arcade.load_texture(
            "images/Samurai/idle/1.png")
        self.texture = self.idle_texture

        self.walk_textures = []
        for i in range(0, 8):
            texture = arcade.load_texture(f"images/Samurai/run/run{i + 1}.png")
            self.walk_textures.append(texture)

        self.shoot_textures = []
        for i in range(0, 6):  # допустим 5 кадров
            texture = arcade.load_texture(
                f"images/Samurai/attack1/{i + 1}.png")
            self.shoot_textures.append(texture)

        self.is_shooting = False
        self.shoot_texture_index = 0
        self.shoot_time = 0
        self.shoot_delay = 0.08
        self.shoot_frame_to_fire = 2
        self.bullet_callback = None

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1  # секунд на кадр

        self.is_walking = False  # Никуда не идём
        self.face_direction = FaceDirection.RIGHT  # и смотрим вправо

    def shoot(self):
        if not self.is_shooting:
            self.is_shooting = True
            self.shoot_texture_index = 0
            self.shoot_time = 0

    def update_animation(self, delta_time: float = 1 / 60):
        """ Обновление анимации """
        if self.is_shooting:
            self.shoot_time += delta_time

            if self.shoot_time >= self.shoot_delay:
                self.shoot_time = 0
                self.shoot_texture_index += 1

                if self.shoot_texture_index >= len(self.shoot_textures):
                    self.is_shooting = False
                    return

            texture = self.shoot_textures[self.shoot_texture_index]
            if self.face_direction == FaceDirection.LEFT:
                texture = texture.flip_horizontally()

            self.texture = texture
            return

        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0

            texture = self.walk_textures[self.current_texture]
            if self.face_direction == FaceDirection.LEFT:
                texture = texture.flip_horizontally()

            self.texture = texture

        # === IDLE ===
        else:
            texture = self.idle_texture
            if self.face_direction == FaceDirection.LEFT:
                texture = texture.flip_horizontally()
            self.texture = texture

    def update(self, delta_time, keys_pressed):
        dx, dy = 0, 0

        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += self.speed
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= self.speed

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.change_x = dx
        self.change_y = dy

        if dx < 0:
            self.face_direction = FaceDirection.LEFT
        elif dx > 0:
            self.face_direction = FaceDirection.RIGHT

        self.is_walking = dx != 0 or dy != 0


class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(
            ":resources:/images/space_shooter/laserBlue01.png",
            scale=0.5
        )

        self.center_x = start_x
        self.center_y = start_y

        angle = math.atan2(target_y - start_y, target_x - start_x)
        self.change_x = math.cos(angle) * 600
        self.change_y = math.sin(angle) * 600
        self.angle = math.degrees(-angle)

    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.set_fullscreen(True)
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.player: arcade.Sprite | None = None
        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT

    def setup(self):
        map_name = "map.tmx"
        self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)
        self.player_list = arcade.SpriteList()
        self.world_width = int(self.tile_map.width *
                               self.tile_map.tile_width * TILE_SCALING)
        self.world_height = int(self.tile_map.height *
                                self.tile_map.tile_height * TILE_SCALING)
        self.floor_list = self.tile_map.sprite_lists["floor"]
        self.wall_list = self.tile_map.sprite_lists["walls"]
        self.decor_list = self.tile_map.sprite_lists["decor"]
        self.collision_list = self.tile_map.sprite_lists["collision"]
        self.player = Hero()
        self.player.center_x = self.world_width // 2
        self.player.center_y = self.world_height // 2
        self.player_list.append(self.player)
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list
        )
        self.keys_pressed = set()
        self.bullet_list = arcade.SpriteList()
        self.enemies = []
        arcade.schedule(self.spawn_enemy, 1)

    def spawn_enemy(self, delta_time):
        """ Создаёт нового врага в случайном месте """
        enemy = {
            'x': random.randint(0, self.world_width),
            'y': random.randint(0, self.world_height),
            'radius': 15,
            'color': arcade.color.RED,
            'speed': random.uniform(50, 150)
        }
        self.enemies.append(enemy)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.floor_list.draw()
        self.wall_list.draw()
        self.decor_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()
        for enemy in self.enemies:
            arcade.draw_circle_filled(enemy['x'], enemy['y'],
                                      enemy['radius'], enemy['color'])

    def on_update(self, delta_time):
        self.player.update(delta_time, self.keys_pressed)
        self.physics_engine.update()
        self.player.update_animation(delta_time)
        self.bullet_list.update(delta_time)
        for enemy in self.enemies:
            dx = self.player.center_x - enemy['x']
            dy = self.player.center_y - enemy['y']
            # Избегаем деления на 0
            dist = max(0.1, math.sqrt(dx * dx + dy * dy))
            enemy['x'] += (dx / dist) * enemy['speed'] * delta_time
            enemy['y'] += (dy / dist) * enemy['speed'] * delta_time
        position = (
            self.player.center_x,
            self.player.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            position,
            0.12  # Плавность следования камеры
        )

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.shoot()

            world_x = x + self.world_camera.position[0] - self.width // 2
            world_y = y + self.world_camera.position[1] - self.height // 2

            bullet = Bullet(
                start_x=self.player.center_x,
                start_y=self.player.center_y,
                target_x=world_x,
                target_y=world_y
            )
            self.bullet_list.append(bullet)


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
