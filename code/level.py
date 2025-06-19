import pygame.sprite
from pygame import Surface

from settings import *
from sprites import Sprite, AnimatedSprite
from player import Player
from groups import AllSprites
from enemies import Drone, Turret
from bullet import Bullet
from background import BackgroundSprite
from random import random

class Level:
    def __init__(self, tmx_map, level_frames, logic_surface):
        self.logic_surface = logic_surface

        # ограничение уровня
        self.level_height = tmx_map.height * TILE_SIZE
        self.level_width = tmx_map.width * TILE_SIZE

        # группы
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.ladder_sprites = pygame.sprite.Group()
        self.drone_path = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.setup(tmx_map, level_frames)

        self.bullet_frames = level_frames['bullet']

    def setup(self, tmx_map, level_frames):
        # задний фон
        backgrounds = level_frames['background']
        for index, background in enumerate(backgrounds):
            background_size = background.get_size()
            scale_factor = self.level_height / background_size[1]

            background = pygame.transform.scale_by(background, scale_factor)
            background_new_size = background.get_size()

            for x in range(0, self.level_width, background_new_size[0]):
                y = 0
                parallax_factor = 0

                if index == 0:
                    parallax_factor = 0.3
                elif index == 1:
                    parallax_factor = 0.5
                elif index == 2:
                    parallax_factor = 0.7

                BackgroundSprite((x, y),
                                 background,
                                 self.all_sprites,
                                 z=Z_LAYERS[f'BG_layer_{index}'],
                                 parallax_factor=parallax_factor
                                 )

        # тайлы
        for layer in ['BG_collision', 'BG_uncollision', 'Ladder']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]

                if layer == 'BG_collision':
                    groups.append(self.collision_sprites)

                elif layer == 'Ladder':
                    groups.append(self.ladder_sprites)

                pos = (x * TILE_SIZE,y * TILE_SIZE)
                z = Z_LAYERS['BG_tiles']

                Sprite(pos, surf, groups, z)

        # обьекты
        for obj in tmx_map.get_layer_by_name('Objects'):
            z = Z_LAYERS['Objects']
            # игрок
            if obj.name == 'player':
                # УБРАТЬ КОНСТАНТУ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.player = Player(
                    pos=(obj.x+450, obj.y-250),
                    groups=self.all_sprites,
                    frames=level_frames['player'],
                    collision_sprites=self.collision_sprites,
                    ladder_sprites=self.ladder_sprites,
                    enemy_sprites=self.enemy_sprites,
                    create_bullet=self.create_bullet
                )

            # все анимационные обьекты заднего фона имеют постфикс '-1' на конце
            elif '-1' in obj.name:
                frames = level_frames['animated_banners'][obj.name[:-2]]
                AnimatedSprite((obj.x, obj.y), frames, self.all_sprites, z=z)

            # статичные детали заднего фона
            else:
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z=z)

        # карта пути для дрона
        for x, y, surf in tmx_map.get_layer_by_name('Enemy_path').tiles():
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            groups = (self.drone_path)
            Sprite(pos, surf, groups, z=Z_LAYERS['None'])

        # враги
        for obj in tmx_map.get_layer_by_name('Enemies'):
            groups = (self.all_sprites, self.enemy_sprites)
            explosion_frames = level_frames['enemy-explosion']
            if obj.name == 'drone-1':
                frames = level_frames['drone']
                Drone((obj.x, obj.y), frames, explosion_frames, groups, self.drone_path)

            if obj.name =='turret-1':
                frames = level_frames['turret']
                Turret((obj.x, obj.y), frames, explosion_frames, groups)

    def create_bullet(self, pos, direction):
        groups = (self.all_sprites, self.bullet_sprites)
        speed = 250
        Bullet(pos, self.bullet_frames, direction, groups, speed)

    def bullet_collision(self):
        # спрайты мира
        for sprite in self.collision_sprites:
            for bullet in self.bullet_sprites:
                if sprite.rect.colliderect(bullet):
                    bullet.dye = True

        # враги
        for enemy in self.enemy_sprites:
            for bullet in self.bullet_sprites:
                if enemy.rect.colliderect(bullet):
                    bullet.dye = True
                    enemy.dye = True

    def check_constaint(self):
        if self.player.hitbox_rect.bottom > self.level_height:
            print('death')

    def run(self, deltatime):
        self.all_sprites.update(deltatime)
        self.bullet_collision()
        self.check_constaint()
        self.logic_surface.fill('black')
        self.all_sprites.draw(self.logic_surface, self.player.hitbox_rect.center, self.level_width, self.level_height)
