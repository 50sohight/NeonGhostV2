import pygame.transform

from settings import *
from timer import Timer

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, frames, direction, groups, speed):
        super().__init__(groups)
        self.frames = frames
        self.fly_frame_index = 0

        self.image = self.frames['shot'][self.fly_frame_index]
        self.direction = direction
        self.rect = self.image.get_frect(center=pos)
        self.speed = speed
        self.z = Z_LAYERS['Main']

        self.dye_frame_index = 0
        self.dye = False

    def move(self, deltatime):
        self.rect.x += self.direction * self.speed * deltatime

    def fly_animate(self, deltatime):
        frames = self.frames['shot']
        self.fly_frame_index += ANIMATION_SPEED * deltatime
        self.image = frames[int(self.fly_frame_index) % len(frames)]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def dye_animate(self, deltatime):
        frames = self.frames['shot-hit']
        self.dye_frame_index += ANIMATION_SPEED * deltatime
        if int(self.dye_frame_index) < len(frames):
            self.image = frames[int(self.dye_frame_index)]
        else:
            self.kill()

    def update(self, deltatime):
        if self.dye:
            self.dye_animate(deltatime)
        else:
            self.move(deltatime)
            self.fly_animate(deltatime)





