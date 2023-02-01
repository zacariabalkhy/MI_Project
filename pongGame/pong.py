import pygame
from constants import BLACK, WHITE, size, SCREEN_HEIGHT, SCREEN_WIDTH
from paddle import Paddle
from ball import Ball
import midi

pygame.init()

# Open new window
screen = pygame.display.set_mode(size)
pygame.display.set_caption("BCIPong!")

# Set up paddles
paddleA = Paddle(WHITE, 100, 10)
paddleA.rect.x = 350
paddleA.rect.y = 100

paddleB = Paddle(WHITE, 100, 10)
paddleB.rect.x = 350
paddleB.rect.y = 600

ball = Ball(WHITE, 10, 10)
ball.rect.x = 345
ball.rect.y = 350

# Collect all game elements (paddles, and ball)
all_sprites_list = pygame.sprite.Group()
all_sprites_list.add(paddleA)
all_sprites_list.add(paddleB)
all_sprites_list.add(ball)

carryOn = True
clock = pygame.time.Clock()

#Initialise player scores
scoreA = 0
scoreB = 0

# Game loop
while carryOn:

    # Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            carryOn = False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_x:
                carryOn = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        paddleA.moveUp(5)
    if keys[pygame.K_s]:
        paddleA.moveDown(5)
    if keys[pygame.K_RIGHT]:
        paddleB.moveRight(5)
    if keys[pygame.K_LEFT]:
        paddleB.moveLeft(5)

    #Check if the ball is bouncing against any of the 4 walls:
    if ball.rect.x >= SCREEN_WIDTH:
        scoreA += 1
        ball.velocity[0] = -ball.velocity[0]
    if ball.rect.x <= 0:
        scoreB += 1
        ball.velocity[0] = -ball.velocity[0]
    if ball.rect.y > SCREEN_HEIGHT:
        ball.velocity[1] = -ball.velocity[1]
    if ball.rect.y < 0:
        ball.velocity[1] = -ball.velocity[1] 
    
    #Detect collisions between the ball and the paddles
    if pygame.sprite.collide_mask(ball, paddleA) or pygame.sprite.collide_mask(ball, paddleB):
      ball.bounce()

    # Game logic
    all_sprites_list.update()

    # Fill background
    screen.fill(BLACK)

    # Draw net
    pygame.draw.line(screen, WHITE, [0, 350], [700, 350], 5)

    # Draw Sprites
    all_sprites_list.draw(screen)

    #Display scores:
    font = pygame.font.Font(None, 74)
    text = font.render(str(scoreA), 1, WHITE)
    screen.blit(text, (10, 390))
    text = font.render(str(scoreB), 1, WHITE)
    screen.blit(text, (10, 270))
    
    # Update screen
    pygame.display.flip()

    # Limit to 60 frames per second
    clock.tick(60) 

pygame.quit()