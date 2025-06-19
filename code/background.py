from settings import *


class BackgroundSprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, *groups, z=0, parallax_factor):
        super().__init__(*groups)
        self.z = z
        self.image = image
        if z == 0:
            self.rect = self.image.get_frect(topleft=pos)
        else:
            self.rect = self.image.get_frect(bottomleft=pos)
        self.parallax_factor = parallax_factor