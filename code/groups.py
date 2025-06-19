import pygame
from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.camera_pos = pygame.math.Vector2(0, 0)
        self.deadzone_size = pygame.Vector2(LOGIC_WIDTH / 3, LOGIC_HEIGHT / 5)

    def draw(self, surf, target_pos, level_width, level_height):
        target_pos = pygame.Vector2(target_pos)
        screen_center = pygame.Vector2(LOGIC_WIDTH // 2, LOGIC_HEIGHT // 2)

        # Смещаем цель чуть выше, чтобы игрок был не по центру, а немного выше
        adjusted_target = pygame.Vector2(target_pos.x, target_pos.y - 50)  # 50 - экспериментальное значение

        camera_center = self.camera_pos + screen_center
        offset = adjusted_target - camera_center

        # Плавное перемещение камеры с deadzone
        if offset.x > self.deadzone_size.x / 2:
            self.camera_pos.x += offset.x - self.deadzone_size.x / 2
        elif offset.x < -self.deadzone_size.x / 2:
            self.camera_pos.x += offset.x + self.deadzone_size.x / 2

        if offset.y > self.deadzone_size.y / 2:
            self.camera_pos.y += offset.y - self.deadzone_size.y / 2
        elif offset.y < -self.deadzone_size.y / 2:
            self.camera_pos.y += offset.y + self.deadzone_size.y / 2

        # Ограничение камеры с учётом смещения
        self.camera_pos.x = max(0, min(self.camera_pos.x, level_width - LOGIC_WIDTH))
        self.camera_pos.y = max(0, min(self.camera_pos.y, level_height - LOGIC_HEIGHT))

        result_offset = -self.camera_pos

        for sprite in sorted(self, key=lambda sprite: sprite.z):
            offset_pos = vector()

            if hasattr(sprite, 'parallax_factor'):
                offset_pos.x = (sprite.rect.left + result_offset.x) * sprite.parallax_factor
                offset_pos.y = sprite.rect.top + result_offset.y
            else:
                offset_pos = sprite.rect.topleft + result_offset

            surf.blit(sprite.image, offset_pos)
