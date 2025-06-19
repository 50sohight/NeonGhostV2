import pygame.sprite

from settings import *
from random import choice
from support import crop_alpha

class Drone(pygame.sprite.Sprite):
    def __init__(self, pos, frames, explosion_frames, groups, collision_sprites):
        super().__init__(groups)

        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.image = crop_alpha(self.frames[int(self.frame_index)])
        self.z = Z_LAYERS['Main']

        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()


        self.direction = choice([-1, 1])

        if self.direction > 0:
            self.image = pygame.transform.flip(self.image, True, False)

        self.base_image = self.image

        self.rotation = False
        self.facing_right = True if self.direction > 0 else False
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 100

        # взрыв
        self.explosion_frames = explosion_frames
        self.dye = False
        self.dye_frame_index = 0
        self.pos = pos

    def reverse_direction(self, deltatime):
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1, 30))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1, 30))

        if (floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0) or (floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0):
            self.direction *= -1
            self.rotation = True

    def move(self, deltatime):
        self.rect.x += self.direction * self.speed * deltatime
        self.pos = self.rect.topleft

    def main_animate(self, deltatime):

        self.frame_index += ANIMATION_SPEED * deltatime

        if int(self.frame_index) < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
            if self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

            self.image = crop_alpha(self.image)
            self.rect = self.image.get_frect(midbottom=self.rect.midbottom)
        else:
            self.frame_index = 0
            self.base_image = pygame.transform.flip(self.base_image, True, False)
            self.image = self.base_image
            self.rect = self.image.get_frect(midbottom=self.rect.midbottom)

            self.rotation = False
            self.facing_right = not self.facing_right

    def dye_animate(self, deltatime):
        self.dye_frame_index += ANIMATION_SPEED * deltatime
        if int(self.dye_frame_index) < len(self.explosion_frames):
            self.image = self.explosion_frames[int(self.dye_frame_index)]
            self.rect.midtop = self.pos
        else:
            self.kill()

    def update(self, deltatime):
        if self.dye:
            self.dye_animate(deltatime)
        else:
            self.reverse_direction(deltatime)
            if self.rotation:
                self.main_animate(deltatime)
            self.move(deltatime)

class Turret(pygame.sprite.Sprite):
    def __init__(self, pos, frames, explosion_frames, groups):
        super().__init__(groups)

        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.z = Z_LAYERS['Main']

        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()

        self.facing_right = False
        self.animation_speed = 12

        # взрыв
        self.explosion_frames = explosion_frames
        self.dye = False
        self.dye_frame_index = 0
        self.pos = pos

    def main_animate(self, deltatime):
        self.frame_index += self.animation_speed * deltatime
        if int(self.frame_index) < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
            if self.frame_index:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.facing_right = not self.facing_right
            self.frame_index = 0

    def dye_animate(self, deltatime):
        self.dye_frame_index += ANIMATION_SPEED * deltatime
        if int(self.dye_frame_index) < len(self.explosion_frames):
            self.image = self.explosion_frames[int(self.dye_frame_index)]
            self.rect.midbottom = self.pos
        else:
            self.kill()

    def update(self, deltatime):
        if self.dye:
            self.dye_animate(deltatime)
        else:
            self.main_animate(deltatime)





