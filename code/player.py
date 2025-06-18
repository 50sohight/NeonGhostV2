from traceback import print_tb

import pygame

from settings import *
from support import crop_alpha

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, frames):
        # инициализация
        super().__init__(groups)
        self.z = Z_LAYERS['Main']

        # изображениеs
        self.frames = frames
        self.frame_index = 0
        self.run_animation_speed = 6
        self.jump_animation_speed = 9
        self.state = 'idle'
        self.old_state = 'idle'
        self.facing_right = True
        self.image = self.frames[self.state][self.frame_index]
        self.image = crop_alpha(self.image)

        # ректенглы
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox_rect = self.rect.copy()
        self.old_rect = self.hitbox_rect.copy()

        # передвижение
        self.direction = vector()
        self.speed = 150
        self.gravity = 1300
        self.jump_speed = -600
        self.jump = False
        self.shooting = False

        # коллизия
        self.collision_sprites = collision_sprites
        self.on_surface = {'floor' : False}

    def input(self):
        keys = pygame.key.get_pressed()

        # обработка лево - право
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True

        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False

        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE]:
            self.jump = True

        if keys[pygame.K_x]:
            self.shoot()

    def shoot(self):
        self.shooting = True
        if self.state == 'run':
            self.frame_index = self.frame_index % len(self.frames[self.state])
        else:
            self.frame_index = 0

    def move(self, deltatime):
        # горизантальное
        self.hitbox_rect.x += self.direction.x * self.speed * deltatime
        self.collision('horizontal')

        # вертикальное
        # законы физики velocity Verlet
        self.direction.y += self.gravity / 2 * deltatime
        self.direction.y = min(self.direction.y, MAX_GRAVITY_VALUE)
        self.hitbox_rect.y += self.direction.y * deltatime
        self.direction.y += self.gravity / 2 * deltatime
        self.collision('vertical')

        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = self.jump_speed
                # чтобы анимация начиналась сначала
                self.frame_index = 0
            self.jump = False

        self.rect.center = self.hitbox_rect.center

    def check_contact(self):
        floor_rect = pygame.Rect((self.hitbox_rect.bottomleft), (self.hitbox_rect.width, 1))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        # коллизии
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 else False

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
                    # лево
                    if self.hitbox_rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.hitbox_rect.left = sprite.rect.right
                    # право
                    elif self.hitbox_rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.hitbox_rect.right = sprite.rect.left

                elif axis == 'vertical':
                    # вверх
                    if self.hitbox_rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.hitbox_rect.top = sprite.rect.bottom
                    # низ
                    elif self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.hitbox_rect.bottom = sprite.rect.top

                    self.direction.y = 0


    def get_state(self):
        self.old_state = self.state

        if self.on_surface['floor']:
            if self.shooting and self.direction.x == 0:
                self.state = 'shoot'
            elif self.shooting and self.direction.x != 0:
                self.state = 'run-shoot'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if self.shooting:
                self.state = 'jump-shoot'
            else:
                if self.direction.y < 0:
                    self.state = 'jump'

                elif self.direction.y > 0:
                    self.state = 'fall'

    def animate(self, deltatime):
        # скорость анимации
        if self.state == 'jump':
            animation_speed = self.jump_animation_speed
        elif self.state in ['run', 'run-shoot']:
            animation_speed = self.run_animation_speed
        else:
            animation_speed = ANIMATION_SPEED

        self.frame_index += animation_speed * deltatime

        # стрельба
        if self.state == 'shoot' and (self.frame_index >= len(self.frames[self.state])):
            self.state = 'idle'
            self.shooting = False

        elif self.state == 'run-shoot' and (self.frame_index >= len(self.frames[self.state])):
            self.state = 'run'
            self.shooting = False

        # обработка прыжка
        if self.state == 'jump' and (self.frame_index >= len(self.frames[self.state])):
            self.state = 'fall'

        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = crop_alpha(self.image)

        # хитбокс и ректенгл
        if self.state in 'run':
            self.rect = self.image.get_frect(bottomright=self.hitbox_rect.bottomright)

        elif self.state == 'run-shoot':
            self.rect = self.image.get_frect(center=self.hitbox_rect.center)

        else:
            self.rect = self.image.get_frect(midbottom=self.hitbox_rect.midbottom)

        # отражение в другую сторону
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

            if self.state in ['run', 'run-shoot']:
                self.rect = self.image.get_frect(bottomleft=self.hitbox_rect.bottomleft)

    def update(self, deltatime):
        self.old_rect = self.hitbox_rect.copy()

        self.input()
        self.move(deltatime)
        self.check_contact()

        self.get_state()
        self.animate(deltatime)
