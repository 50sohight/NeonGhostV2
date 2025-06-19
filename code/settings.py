import pygame, sys

from pygame.math import Vector2 as vector

# размеры для отрисовки
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

# размеры логики и просчета
LOGIC_WIDTH, LOGIC_HEIGHT = 640, 360

MAX_DELTATIME = round(1/30, 3) # deltatime при 30 фпс

TILE_SIZE = 16

ANIMATION_SPEED = 6
MAX_GRAVITY_VALUE = 3300


# layers
Z_LAYERS = {
    'None' : -1,
    'BG_layer_0' : 0,
    'BG_layer_1' : 1,
    'BG_layer_2' : 2,
    'BG_tiles' : 3,
    'Objects' : 4,
    'Main' : 5
}