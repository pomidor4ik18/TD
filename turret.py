import pygame as pg
import math
import constants as c
from turret_data import TURRET_DATA

class Turret(pg.sprite.Sprite):
    """
    Класс Turret представляет турель в игре, которая может стрелять по врагам и обновляться.
    """

    def __init__(self, sprite_sheets, tile_x, tile_y, shot_fx):
        """
        Инициализация турели.

        Args:
            sprite_sheets (list): Список спрайтов для анимации турели.
            tile_x (int): Координата X на сетке тайлов.
            tile_y (int): Координата Y на сетке тайлов.
            shot_fx (pygame.mixer.Sound): Звук выстрела.
        """
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None

        self.tile_x = tile_x
        self.tile_y = tile_y
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE

        self.shot_fx = shot_fx

        self.sprite_sheets = sprite_sheets
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()

        self.angle = 90
        self.original_image = self.animation_list[self.frame_index]
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def load_images(self, sprite_sheet):
        """
        Загрузка изображений из спрайт-листа.

        Args:
            sprite_sheet (pygame.Surface): Спрайт-лист для текущего уровня турели.

        Returns:
            list: Список изображений для анимации турели.
        """
        size = sprite_sheet.get_height()
        animation_list = []
        for x in range(c.ANIMATION_STEPS):
            temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
            animation_list.append(temp_img)
        return animation_list

    def update(self, enemy_group, world):
        """
        Обновление состояния турели, включая выбор цели и анимацию.

        Args:
            enemy_group (pygame.sprite.Group): Группа врагов.
            world (World): Объект игрового мира.
        """
        if self.target:
            self.play_animation()
        else:
            if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
                self.pick_target(enemy_group)

    def pick_target(self, enemy_group):
        """
        Выбор ближайшей цели в радиусе действия турели.

        Args:
            enemy_group (pygame.sprite.Group): Группа врагов.
        """
        for enemy in enemy_group:
            if enemy.health > 0:
                x_dist = enemy.pos[0] - self.x
                y_dist = enemy.pos[1] - self.y
                dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                if dist < self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                    self.target.health -= c.DAMAGE
                    self.shot_fx.play()
                    break

    def play_animation(self):
        """
        Воспроизведение анимации стрельбы турели.
        """
        self.original_image = self.animation_list[self.frame_index]
        if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                self.last_shot = pg.time.get_ticks()
                self.target = None

    def upgrade(self):
        """
        Улучшение турели: увеличение уровня, радиуса действия и обновление изображений.
        """
        self.upgrade_level += 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.original_image = self.animation_list[self.frame_index]

        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def draw(self, surface):
        """
        Отрисовка турели и её радиуса действия (если выделена).

        Args:
            surface (pygame.Surface): Поверхность, на которой нужно нарисовать турель.
        """
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)
