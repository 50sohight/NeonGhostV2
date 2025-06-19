from settings import *

class BackgroundSprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, *groups, z=0, parallax_factor):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)
        self.z = z
        self.parallax_factor = parallax_factor
    