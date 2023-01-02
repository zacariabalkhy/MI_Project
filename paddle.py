import pygame
from constants import BLACK, SCREEN_HEIGHT

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
    
    def moveUp(self, pixels):
        self.rect.y -= pixels
        if self.rect.y < 0:
            self.rect.y = 0

    
    def moveDown(self, pixels):
        self.rect.y += pixels
        if self.rect.y + self.rect.size[1] > SCREEN_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - self.rect.size[1]

