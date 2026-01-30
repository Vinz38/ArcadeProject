from arcade.color import PINK_PEARL, BLACK_OLIVE
from pyglet.graphics import Batch
import arcade
import math
import enum
import random
import arcade.gui as gui

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Спрайтовый герой"
TILE_SCALING = 4


class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Основные характеристики
        self.scale = TILE_SCALING * 0.5
        self.speed = 4
        self.health = 100

        self.idle_texture_down = arcade.load_texture("images/VqqmpWW/Vqqmp_idle/down/1.png")
        self.idle_texture_up = arcade.load_texture("images/VqqmpWW/Vqqmp_idle/top/1.png")
        self.idle_texture_left = arcade.load_texture("images/VqqmpWW/Vqqmp_idle/left/1.png")
        self.idle_texture_right = arcade.load_texture("images/VqqmpWW/Vqqmp_idle/right/1.png")
        self.texture = self.idle_texture_down

        self.walk_textures_down = []
        self.walk_textures_up = []
        self.walk_textures_left = []
        self.walk_textures_right = []

        for i in range(0, 6):
            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_walk/down/{i + 1}.png")
            self.walk_textures_down.append(texture)

            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_walk/top/{i + 1}.png")
            self.walk_textures_up.append(texture)

            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_walk/left/{i + 1}.png")
            self.walk_textures_left.append(texture)

            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_walk/right/{i + 1}.png")
            self.walk_textures_right.append(texture)

        self.shoot_textures_down = []
        self.shoot_textures_up = []
        self.shoot_textures_left = []
        self.shoot_textures_right = []

        for i in range(0, 11):
            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_attack/down/{i + 1}.png")
            self.shoot_textures_down.append(texture)
        for i in range(0, 11):
            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_attack/top/{i + 1}.png")
            self.shoot_textures_up.append(texture)
        for i in range(0, 11):
            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_attack/left/{i + 1}.png")
            self.shoot_textures_left.append(texture)
        for i in range(0, 11):
            texture = arcade.load_texture(f"images/VqqmpWW/Vqqmp_attack/right/{i + 1}.png")
            self.shoot_textures_right.append(texture)

        self.is_shooting = False
        self.shoot_texture_index = 0
        self.shoot_time = 0
        self.shoot_delay = 0.08
        self.bullet_fired = False
        self.bullet_callback = None
        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1

        self.is_walking = False
        self.face_direction = FaceDirection.DOWN

    def shoot(self, target_x, target_y):
        if not self.is_shooting:
            self.is_shooting = True
            self.shoot_texture_index = 0
            self.shoot_time = 0
            self.bullet_fired = False

            # Сохраняем цель для выстрела
            self.target_x = target_x
            self.target_y = target_y

            # Устанавливаем направление в зависимости от положения цели
            dx = target_x - self.center_x
            dy = target_y - self.center_y

            # Определяем основное направление (горизонтальное или вертикальное)
            if abs(dx) > abs(dy):
                if dx < 0:
                    self.face_direction = FaceDirection.LEFT
                else:
                    self.face_direction = FaceDirection.RIGHT
            else:
                if dy < 0:
                    self.face_direction = FaceDirection.DOWN
                else:
                    self.face_direction = FaceDirection.UP

    def update_animation(self, delta_time: float = 1 / 60):
        if self.is_shooting:
            self.shoot_time += delta_time
            if self.shoot_time >= self.shoot_delay:
                self.shoot_time = 0
                self.shoot_texture_index += 1

                # Выбираем текстуру атаки в зависимости от направления
                if self.face_direction == FaceDirection.DOWN:
                    textures = self.shoot_textures_down
                elif self.face_direction == FaceDirection.UP:
                    textures = self.shoot_textures_up
                elif self.face_direction == FaceDirection.LEFT:
                    textures = self.shoot_textures_left
                else:  # RIGHT
                    textures = self.shoot_textures_right

                # Выпускаем пулю на 10-м кадре анимации (индекс 9)
                if not self.bullet_fired and self.shoot_texture_index >= 9:
                    self.bullet_fired = True
                    if self.bullet_callback:
                        self.bullet_callback(self.target_x, self.target_y)

                # Устанавливаем текущую текстуру атаки
                if self.shoot_texture_index < len(textures):
                    self.texture = textures[self.shoot_texture_index]
                else:
                    # Если дошли до конца анимации, завершаем стрельбу
                    self.is_shooting = False
                    self.bullet_fired = False
                    self.shoot_texture_index = 0
            return

        # Анимация ходьбы (если не стреляем)
        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1

            # Выбираем текстуры ходьбы в зависимости от направления
            if self.face_direction == FaceDirection.DOWN:
                if self.current_texture >= len(self.walk_textures_down):
                    self.current_texture = 0
                self.texture = self.walk_textures_down[self.current_texture]
            elif self.face_direction == FaceDirection.UP:
                if self.current_texture >= len(self.walk_textures_up):
                    self.current_texture = 0
                self.texture = self.walk_textures_up[self.current_texture]
            elif self.face_direction == FaceDirection.LEFT:
                if self.current_texture >= len(self.walk_textures_left):
                    self.current_texture = 0
                self.texture = self.walk_textures_left[self.current_texture]
            elif self.face_direction == FaceDirection.RIGHT:
                if self.current_texture >= len(self.walk_textures_right):
                    self.current_texture = 0
                self.texture = self.walk_textures_right[self.current_texture]

        # Анимация стояния на месте
        else:
            self.current_texture = 0
            if self.face_direction == FaceDirection.DOWN:
                self.texture = self.idle_texture_down
            elif self.face_direction == FaceDirection.UP:
                self.texture = self.idle_texture_up
            elif self.face_direction == FaceDirection.LEFT:
                self.texture = self.idle_texture_left
            elif self.face_direction == FaceDirection.RIGHT:
                self.texture = self.idle_texture_right

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

        # Обновляем направление в зависимости от движения (только если не атакуем)
        if not self.is_shooting:
            if dx < 0:
                self.face_direction = FaceDirection.LEFT
            elif dx > 0:
                self.face_direction = FaceDirection.RIGHT
            elif dy > 0:
                self.face_direction = FaceDirection.UP
            elif dy < 0:
                self.face_direction = FaceDirection.DOWN

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

    def update(self, delta_time: float = 1 / 60):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        if (self.center_x < 0 or self.center_x > SCREEN_WIDTH * 10 or
                self.center_y < 0 or self.center_y > SCREEN_HEIGHT * 10):
            self.remove_from_sprite_lists()


class Monster(arcade.Sprite):
    def __init__(self, monster_x, monster_y, player):
        super().__init__(":resources:/images/enemies/slimePurple.png", scale=0.5)
        self.monster_health = 10
        self.monster_speed = random.uniform(50, 150)
        self.center_x = monster_x
        self.center_y = monster_y
        self.player = player

        self.can_attack = True
        self.attack_cooldown = 1.0
        self.attack_timer = 0
        self.attack_damage = 5

    def update(self, delta_time: float = 1 / 60):
        if not self.can_attack:
            self.attack_timer += delta_time
            if self.attack_timer >= self.attack_cooldown:
                self.can_attack = True
                self.attack_timer = 0
        dx = self.player.center_x - self.center_x
        dy = self.player.center_y - self.center_y
        dist = max(0.1, math.sqrt(dx * dx + dy * dy))  # Избегаем деления на 0
        self.center_x += (dx / dist) * self.monster_speed * delta_time
        self.center_y += (dy / dist) * self.monster_speed * delta_time


class MyGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = gui.UIManager()
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.player: arcade.Sprite | None = None
        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT
        self.score = 0
        self.exp = 0
        self.lvl = 0
        self.aura_radius = 100
        self.aura_damage = 1
        # в будущем добавить
        self.is_aura = False
        self.tile_map = None
        self.player_list = None
        self.monster_list = None
        self.bullet_list = None
        self.batch = None
        self.floor_list = None
        self.wall_list = None
        self.decor_list = None
        self.collision_list = None
        self.physics_engine = None
        self.physics_engine_2 = None
        self.keys_pressed = set()
        self.can_shoot = True
        # в будущем добавить self.hard = [1, 1]
        self.setup()

    def setup(self):
        map_name = "map.tmx"
        self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)
        # списки спрайтов
        self.player_list = arcade.SpriteList()
        self.monster_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.batch = Batch()
        # мировые координаты
        self.world_width = int(self.tile_map.width * self.tile_map.tile_width * TILE_SCALING)
        self.world_height = int(self.tile_map.height * self.tile_map.tile_height * TILE_SCALING)
        # карта из tiled
        self.floor_list = self.tile_map.sprite_lists["floor"]
        self.wall_list = self.tile_map.sprite_lists["walls"]
        self.decor_list = self.tile_map.sprite_lists["decor"]
        self.collision_list = self.tile_map.sprite_lists["collision"]
        # игрок
        self.player = Hero()
        self.player.center_x = self.world_width // 2
        self.player.center_y = self.world_height // 2
        self.player_list.append(self.player)
        self.player.bullet_callback = self.create_bullet
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list)
        self.physics_engine_2 = arcade.PhysicsEngineSimple(
            self.monster_list, self.collision_list)
        self.keys_pressed = set()
        self.world_camera.position = (self.player.center_x, self.player.center_y)
        # монстры
        arcade.schedule(self.spawn_enemy, 1)
        # кд пули
        self.can_shoot = True
        self.shoot_cooldown = 1

    def create_bullet(self, target_x, target_y):
        if self.can_shoot:
            bullet = Bullet(self.player.center_x, self.player.center_y, target_x, target_y)
            self.bullet_list.append(bullet)
            self.can_shoot = False
            arcade.schedule(lambda delta_time: self.weapon_ready(delta_time), self.shoot_cooldown)

    def spawn_enemy(self, delta_time):
        x = random.randint(0, self.world_width)
        y = random.randint(0, self.world_height)
        monster = Monster(monster_x=x, monster_y=y, player=self.player)
        self.monster_list.append(monster)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.floor_list.draw()
        self.wall_list.draw()
        self.decor_list.draw()
        if self.is_aura:
            arcade.draw_circle_outline(self.player.center_x, self.player.center_y, self.aura_radius,
                                       arcade.color.RED_DEVIL,
                                       3)
        self.player_list.draw()
        self.bullet_list.draw()
        self.monster_list.draw()
        self.gui_camera.use()
        arcade.draw_rect_filled(arcade.rect.XYWH(40, SCREEN_HEIGHT - 60, 150, 150), color=arcade.color.DARK_BYZANTIUM)
        self.batch.draw()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.player.update(delta_time, self.keys_pressed)
        self.physics_engine.update()
        self.player.update_animation(delta_time)
        self.bullet_list.update(delta_time)
        # удары монстров
        for monster in self.monster_list:
            # в будущем добавить
            # monster.monster_health += self.hard[0] * delta_time
            # monster.attack_damage += self.hard[0] * delta_time
            if self.is_aura:
                if (self.player.center_x - monster.center_x) ** 2 + (
                        self.player.center_y - monster.center_y) ** 2 <= self.aura_radius ** 2:
                    monster.monster_health -= self.aura_damage * delta_time
        for monster in self.monster_list:
            if arcade.check_for_collision(self.player, monster):
                if monster.can_attack:
                    self.player.health -= monster.attack_damage
                    monster.can_attack = False
                    monster.attack_timer = 0
                    if self.player.health <= 0:
                        self.window.show_view(StartView())
        # удары по монстрам
        if self.is_aura:
            for monster in self.monster_list:
                if (self.player.center_x - monster.center_x) ** 2 + (
                        self.player.center_y - monster.center_y) ** 2 <= self.aura_radius ** 2:
                    monster.monster_health -= self.aura_damage * delta_time
                    self.check_monstr(monster)
        for bullet in self.bullet_list:
            enemy_hit_list = arcade.check_for_collision_with_list(bullet, self.monster_list)
            for enemy in enemy_hit_list:
                enemy.monster_health -= 5
                self.check_monstr(enemy)
                bullet.remove_from_sprite_lists()
        self.monster_list.update(delta_time)
        # камера
        position = (
            self.player.center_x,
            self.player.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            0.6
        )
        # Обновляем текст
        self.pl_h_text = arcade.Text(f"HP: {self.player.health}", 10, SCREEN_HEIGHT - 30,
                                     arcade.color.SUNSET_ORANGE, 20, font_name="Calibri", batch=self.batch)
        self.score_text = arcade.Text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 120,
                                      arcade.color.LIGHT_GRAY, 20, font_name="Calibri", batch=self.batch)
        self.exp_text = arcade.Text(f"Exp: {self.exp}", 10, SCREEN_HEIGHT - 60,
                                    arcade.color.CADET_BLUE, 20, font_name="Calibri", batch=self.batch)
        self.lvl_text = arcade.Text(f"Level: {self.lvl}", 10, SCREEN_HEIGHT - 90,
                                    arcade.color.LIGHT_GRAY, 20, font_name="Calibri", batch=self.batch)

    def on_close(self):
        arcade.unschedule(self.spawn_enemy)
        arcade.close_window()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            world_x = self.world_camera.position[0] + (x - self.window.width / 2)
            world_y = self.world_camera.position[1] + (y - self.window.height / 2)
            self.player.shoot(world_x, world_y)

    def weapon_ready(self, delta_time):
        self.can_shoot = True
        arcade.unschedule(self.weapon_ready)

    def check_monstr(self, enemy):
        if enemy.monster_health <= 0:
            enemy.remove_from_sprite_lists()
            self.score += 1
            self.exp += 10
            if self.exp == 100:
                self.lvl += 1
                self.exp = 0
                BUFF = [
                    ('move speed + 1', ('speed', 1)),
                    ('hp 15', ('health', 15)),
                    ('move speed + 1.5', ('speed', 1.5)),
                    ('hp 10', ('health', 10))
                ]

                v_box = gui.UIBoxLayout(space_between=20)
                l1 = random.sample(BUFF, k=3)
                first_button = gui.UIFlatButton(text=l1[0][0], width=200, style={
                    "normal": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.BLUE,
                    },
                    "hover": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.DARK_BLUE,
                    },
                    "press": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.BLUE_GRAY,
                    }})

                @first_button.event("on_click")
                def on_click_f(event):
                    buff_type, value = l1[0][1]
                    if buff_type == 'speed':
                        self.player.speed += value
                    elif buff_type == 'health':
                        self.player.health += value
                    self.ui_manager.remove(anchor)

                second_button = gui.UIFlatButton(text=l1[1][0], width=200, style={
                    "normal": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.BLUE,
                    },
                    "hover": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.DARK_BLUE,
                    },
                    "press": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.BLUE_GRAY,
                    }})

                @second_button.event("on_click")
                def on_click_sec(event):
                    buff_type, value = l1[1][1]
                    if buff_type == 'speed':
                        self.player.speed += value
                    elif buff_type == 'health':
                        self.player.health += value
                    self.ui_manager.remove(anchor)

                third_button = gui.UIFlatButton(text=l1[2][0], width=200, style={
                    "normal": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.BLUE,
                    },
                    "hover": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.DARK_BLUE,
                    },
                    "press": {
                        "font_name": "Calibri",
                        "font_size": 16,
                        "font_color": arcade.color.BLACK,
                        "bg_color": arcade.color.BLUE_GRAY,
                    }})

                @third_button.event("on_click")
                def on_click_t(event):
                    buff_type, value = l1[2][1]
                    if buff_type == 'speed':
                        self.player.speed += value
                    elif buff_type == 'health':
                        self.player.health += value
                    self.ui_manager.remove(anchor)

                v_box.add(first_button)
                v_box.add(second_button)
                v_box.add(third_button)

                anchor = gui.UIAnchorLayout()
                anchor.add(
                    anchor_x="center_x",
                    anchor_y="center_y",
                    align_y=-SCREEN_HEIGHT * 0.2,
                    child=v_box
                )
                self.ui_manager.add(anchor)

    def on_show_view(self):
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()


class StartView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.batch = Batch()
        start_text = arcade.Text("Спрайтовый герой", self.window.width / 2, self.window.height / 2,
                                 arcade.color.WHITE, font_size=50, anchor_x="center", batch=self.batch)
        any_key_text = arcade.Text("Any key to start",
                                   self.window.width / 2, self.window.height / 2 - 75,
                                   arcade.color.GRAY, font_size=20, anchor_x="center", batch=self.batch)
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        self.window.show_view(MyGame())


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
