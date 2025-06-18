import pygame
from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.camera_pos = pygame.math.Vector2(0, 0)
        self.deadzone_size = pygame.Vector2(LOGIC_WIDTH / 3, LOGIC_HEIGHT / 5)

    def draw(self, surf, target_pos):
        target_pos = pygame.Vector2(target_pos)
        screen_center = pygame.Vector2(LOGIC_WIDTH // 2, LOGIC_HEIGHT // 2)

        camera_center = self.camera_pos + screen_center

        offset = target_pos - camera_center

        if offset.x > self.deadzone_size.x / 2:
            self.camera_pos.x += offset.x - self.deadzone_size.x / 2

        elif offset.x < -self.deadzone_size.x / 2:
            self.camera_pos.x += offset.x + self.deadzone_size.x / 2

        if offset.y > self.deadzone_size.y / 2:
            self.camera_pos.y += offset.y - self.deadzone_size.y / 2
        elif offset.y < -self.deadzone_size.y / 2:
            self.camera_pos.y += offset.y + self.deadzone_size.y / 2

        result_offcet = -self.camera_pos

        for sprite in sorted(self, key=lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + result_offcet
            surf.blit(sprite.image, offset_pos)
