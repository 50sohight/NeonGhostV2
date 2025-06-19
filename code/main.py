import pygame

from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from support import *

class Game:
    def __init__(self):
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Neon-Ghost')

        self.clock = pygame.time.Clock()

        self.import_assets()

        self.logic_surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))

        self.tmx_maps = {0: load_pygame('../data/levels/level0.tmx')}

        self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.logic_surface)

    def import_assets(self):
        self.level_frames = {
            'animated_banners' : import_sub_folders('../graphics/warped city files/ENVIRONMENT/props'),
            'player' : import_sub_folders('../graphics/warped city files/SPRITES/player'),
            'bullet': import_sub_folders('../graphics/warped city files/SPRITES/misc/bullet'),

            'drone' : import_folder('../graphics/warped city files/SPRITES/misc/drone'),
            'turret' : import_folder('../graphics/warped city files/SPRITES/misc/turret'),
            'enemy-explosion' : import_folder('../graphics/warped city files/SPRITES/misc/enemy-explosion'),


            'antenna' : import_image('../graphics/warped city files/ENVIRONMENT/props/antenna.png'),
            'banner-arrow' : import_image('../graphics/warped city files/ENVIRONMENT/props/banner-arrow.png'),
            'hotel-sign' : import_image('../graphics/warped city files/ENVIRONMENT/props/hotel-sign.png'),
            'banner-floor' : import_image('../graphics/warped city files/ENVIRONMENT/props/banner-floor.png'),
            'banner-open' : import_image('../graphics/warped city files/ENVIRONMENT/props/banner-open.png'),
            'banners.png' : import_image('../graphics/warped city files/ENVIRONMENT/props/banners.png'),
            'banner-small' : import_image('../graphics/warped city files/ENVIRONMENT/props/banner-small.png')

        }

    def run(self):
        while True:
            deltatime = self.clock.tick() / 1000 # обработка зависания игры
            deltatime = min(deltatime, MAX_DELTATIME)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.logic_surface.fill('black')

            self.current_stage.run(deltatime)
            scaled_logic_surface = pygame.transform.scale(self.logic_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.display_surface.blit(scaled_logic_surface, (0,0))

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()