import os
import random
import pygame
from os import listdir
from os.path import isfile, join

# Variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (255, 255, 255)
FPS = 60
PLAYER_VEL = 5

# Initalize
pygame.init()
clock = pygame.time.Clock()

# Create the screen
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Title and icon
pygame.display.set_caption("Platformer")



# Function
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))

def main(window):
    run = True
    while run == True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
    


    pygame.quit()
    quit()





if __name__ == "__main__":
    main(window)