import pygame
from Tools.scripts.summarize_stats import print_title

from settings import *
from support import crop_alpha
from bullet import Bullet
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, enemy_sprites, ladder_sprites, frames, create_bullet):
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
        self.crouch = False

        self.clambing_speed = 100
        self.try_clambing = False
        self.on_ladder = False
        self.vector_clambing = None

        # стрельба
        self.try_shoot = False
        self.can_shoot = True
        self.shooting = False
        self.create_bullet = create_bullet

        # коллизия
        self.collision_sprites = collision_sprites
        self.enemy_sprites = enemy_sprites
        self.ladder_sprites = ladder_sprites
        self.on_surface = {'floor' : False}

        # урон
        self.knockback = vector(0, 0)
        self.knockback_strength = vector(200, 15)  # скорость откидывания

        # таймеры
        self.timers = {
            'shoot_timer' : Timer(800, self.enable_shoot),
            'hurt' : Timer(1200),
            'knockback' : Timer(300)
        }

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True

        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False

        elif keys[pygame.K_c]:
            self.direction.x = 0
            self.crouch = True

        else:
            self.direction.x = 0
            self.crouch = False

        if keys[pygame.K_UP]:
            self.vector_climbing = 'up'
            self.try_clambing = True

        elif keys[pygame.K_DOWN]:
            self.vector_climbing = 'down'
            self.try_clambing = True

        else:
            self.vector_climbing = None
            self.try_clambing = False

        if keys[pygame.K_SPACE]:
            self.jump = True

        if keys[pygame.K_x]:
            self.try_shoot = True

    def enable_shoot(self):
        self.can_shoot = True

    def shoot(self):
        self.try_shoot = False

        if self.can_shoot:
            self.shooting = True
            self.can_shoot = False
            self.timers['shoot_timer'].activate()

            bullet_direction = 1 if self.facing_right is True else -1

            # опустить выстрел

            pos = None
            vector_modification = vector()

            if 'run' in self.state:
                vector_modification = vector(7, -15)
            elif self.state == 'idle':
                vector_modification = vector(0, -18)
            elif self.state == 'crouch':
                vector_modification = vector(0)

            if bullet_direction > 0:
                pos = self.rect.midright + vector_modification
            else:
                pos = self.rect.midleft + vector_modification

            self.create_bullet(pos, bullet_direction)

            # для корректной анимации при беге
            if self.state == 'run':
                self.frame_index = self.frame_index % len(self.frames[self.state])
            else:
                self.frame_index = 0

    def move(self, deltatime):
        if self.timers['knockback'].active:
            self.hitbox_rect.x += self.knockback.x * deltatime
            self.hitbox_rect.y += self.knockback.y * deltatime
        else:
            # горизантальное
            self.hitbox_rect.x += self.direction.x * self.speed * deltatime
            self.collision('horizontal')

            # вертикальное
            # законы физики velocity Verlet

            if self.on_ladder and self.direction.x != 0:
                self.direction.y = 0
                self.on_ladder = False

            if self.on_ladder:
                self.hitbox_rect.y += self.direction.y * self.clambing_speed * deltatime
                self.direction.y = 0
                self.collision('vertical')

            else:
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

    def climbing(self):
        if pygame.sprite.spritecollideany(self, self.ladder_sprites):
            self.on_ladder = True
            if self.vector_climbing == 'up':
                self.direction.y = -1
            elif self.vector_climbing == 'down':
                self.direction.y = 1
            else:
                self.direction.y = 0
        else:
            self.on_ladder = False

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
                    if self.on_ladder:
                        # низ
                        if self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                            self.hitbox_rect.bottom = sprite.rect.top
                    else:
                        # вверх
                        if self.hitbox_rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                            self.hitbox_rect.top = sprite.rect.bottom
                        # низ
                        elif self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                            self.hitbox_rect.bottom = sprite.rect.top

                    self.direction.y = 0

    def get_damage(self):
        if not self.timers['hurt'].active:
            for enemy in self.enemy_sprites:
                if enemy.rect.colliderect(self.hitbox_rect):
                    self.timers['hurt'].activate()

                    if self.on_surface['floor']:
                        knockback_strength = vector(200, -15)
                        if self.rect.centerx < enemy.rect.centerx:
                            knockback_strength = vector(-200, -15)
                        else:
                            knockback_strength = vector(200, -15)
                        self.knockback = knockback_strength
                    else:
                        knockback_strength = vector(50, -0)
                        if self.rect.centerx < enemy.rect.centerx:
                            knockback_strength = vector(-50, 0)
                        else:
                            knockback_strength = vector(50, 0)
                        self.knockback = knockback_strength

                    self.timers['knockback'].activate()

    def get_state(self):
        self.old_state = self.state

        if self.on_surface['floor']:

            if self.shooting:
                if self.crouch and self.direction.x == 0:
                    self.state = 'crouch'
                elif not self.crouch and (self.direction.x == 0):
                    self.state = 'shoot'
                elif self.direction.x != 0:
                    self.state = 'run-shoot'
            else:
                if self.crouch and self.direction.x == 0:
                    self.state = 'crouch'
                elif not self.crouch and self.direction.x == 0:
                    self.state = 'idle'
                else:
                    self.state = 'run'

        else:

            if self.shooting:
                self.state = 'jump-shoot'

            else:
                if self.on_ladder:
                    self.state = 'climb'
                elif self.direction.y < 0 and not self.on_ladder:
                    self.state = 'jump'
                elif self.direction.y > 0:
                    self.state = 'fall'

        if self.timers['knockback'].active:
            self.state = 'hurt'

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

        elif self.state == 'climb':
            self.rect = self.image.get_frect(midbottom=self.hitbox_rect.midbottom)

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
        self.get_state()
        if self.try_clambing:
            self.climbing()
        self.move(deltatime)
        if self.try_shoot:
            self.shoot()
        self.check_contact()
        self.get_damage()

        self.animate(deltatime)

        for timer in self.timers.values():
            timer.update()
