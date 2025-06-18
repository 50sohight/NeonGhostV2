import pygame.sprite
from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups=None, z=Z_LAYERS['Main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = z


class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups=None, z=Z_LAYERS['Main'], animation_speed=ANIMATION_SPEED):
        self.frames = frames
        self.frame_index = 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, deltatime):
        self.frame_index += self.animation_speed * deltatime
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, deltatime):
        self.animate(deltatime)