import pygame
from constants import BLACK, WHITE, size
from paddle import Paddle
from ball import Ball

pygame.init()

# Open new window
screen = pygame.display.set_mode(size)
pygame.display.set_caption("BCIPong!")

# Set up paddles
paddleA = Paddle(WHITE, 10, 100)
paddleA.rect.x = 20
paddleA.rect.y = 200

paddleB = Paddle(WHITE, 10, 100)
paddleB.rect.x = 670
paddleB.rect.y = 200

ball = Ball(WHITE, 10, 10)
ball.rect.x = 345
ball.rect.y = 195

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
    if keys[pygame.K_UP]:
        paddleB.moveUp(5)
    if keys[pygame.K_DOWN]:
        paddleB.moveDown(5)

    #Check if the ball is bouncing against any of the 4 walls:
    if ball.rect.x >= 690:
        scoreA += 1
        ball.velocity[0] = -ball.velocity[0]
    if ball.rect.x <= 0:
        scoreB += 1
        ball.velocity[0] = -ball.velocity[0]
    if ball.rect.y > 490:
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
    pygame.draw.line(screen, WHITE, [349, 0], [349, 500], 5)

    # Draw Sprites
    all_sprites_list.draw(screen)

    #Display scores:
    font = pygame.font.Font(None, 74)
    text = font.render(str(scoreA), 1, WHITE)
    screen.blit(text, (250,10))
    text = font.render(str(scoreB), 1, WHITE)
    screen.blit(text, (420,10))
    
    # Update screen
    pygame.display.flip()

    # Limit to 60 frames per second
    clock.tick(60) 

pygame.quit()