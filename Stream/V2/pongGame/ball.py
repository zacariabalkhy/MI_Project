import pygame
from random import randint, uniform
import math

from .constants import BLACK

class Ball(pygame.sprite.Sprite):

    def __init__(self, color, width, height):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        # Draw ball
        pygame.draw.rect(self.image, color, [0, 0, width, height])

        # initialize random velocity
        self.velocity = [uniform(2,6), uniform(0,5)]

        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    def bounce(self):
        self.velocity[1] = -self.velocity[1]
        newYvelocity = self.velocity[0] + uniform(-2,2)
        if abs(newYvelocity) > 5:
            newYvelocity += -1 if (newYvelocity >= 0) else 1
        self.velocity[0] = newYvelocity