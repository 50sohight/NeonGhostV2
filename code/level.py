import pygame.sprite
from pygame import Surface

from settings import *
from sprites import Sprite, AnimatedSprite
from player import Player
from groups import AllSprites
from enemies import Drone, Turret

class Level:
    def __init__(self, tmx_map, level_frames, logic_surface):
        self.logic_surface = logic_surface

        # группы
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.drone_path = pygame.sprite.Group()
        self.drone_sprites = pygame.sprite.Group()
        self.setup(tmx_map, level_frames)

    def setup(self, tmx_map, level_frames):
        # тайлы
        for layer in ['BG_collision', 'BG_uncollision']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'BG_collision':
                    groups.append(self.collision_sprites)

                pos = (x * TILE_SIZE,y * TILE_SIZE)
                z = Z_LAYERS[layer]

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
                    collision_sprites=self.collision_sprites,
                    frames=level_frames['player']
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
            if obj.name == 'drone-1':
                frames = level_frames['drone']
                groups = (self.all_sprites, self.drone_sprites)
                Drone((obj.x, obj.y), frames, groups, self.drone_path)

            if obj.name =='turret-1':
                frames = level_frames['turret']
                groups = (self.all_sprites, self.drone_sprites)
                Turret((obj.x, obj.y), frames, groups)

    def run(self, deltatime):
        self.all_sprites.update(deltatime)
        self.logic_surface.fill('black')
        self.all_sprites.draw(self.logic_surface, self.player.hitbox_rect.center)
