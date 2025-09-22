import os
import random
import pygame
from os import listdir
from os.path import isfile, join

# Variables
WIDTH = 800
HEIGHT = 600
BG_COLOR = (255, 255, 255)
FPS = 60
PLAYER_VEL = 5

# Initalize
pygame.init()

# Create the screen
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Title and icon
pygame.display.set_caption("Platformer")



# Function
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    
    return tiles, image


def draw(window, background, bg_image):
    for tile in background:
        window.blit(bg_image, tile)

    pygame.display.update()



def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")


    run = True
    while run == True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        draw(window, background, bg_image)
    


    pygame.quit()
    quit()





if __name__ == "__main__":
    main(window)