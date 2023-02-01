import pygame
from constants import BLACK, SCREEN_HEIGHT, SCREEN_WIDTH

class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        # Call parent class constructor
        super().__init__()

        # Pass in color, width, and height of paddle
        # Set background color to be transparent
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        pygame.draw.rect(self.image, color, [0, 0, width, height])

        self.rect = self.image.get_rect()
    
    def moveRight(self, pixels):
        self.rect.x += pixels
        if self.rect.x + self.rect.size[0] > SCREEN_WIDTH:
            self.rect.x = SCREEN_WIDTH - self.rect.size[0]

    
    def moveLeft(self, pixels):
        self.rect.x -= pixels
        if self.rect.x < 0:
            self.rect.x = 0