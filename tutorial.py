import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1200, 800
FPS = 60
PLAYER_VEL = 5

PIXEL_FONT = pygame.font.Font("assets/Fonts/pixel.ttf", 16)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False, frames=None):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        if frames is not None:
            frame_w = sprite_sheet.get_width() // frames
            for i in range(frames):
                surface = pygame.Surface((frame_w, height), pygame.SRCALPHA, 32)
                rect = pygame.Rect(i * frame_w, 0, frame_w, height)
                surface.blit(sprite_sheet, (0, 0), rect)
                sprites.append(pygame.transform.scale2x(surface))
        else:
            for i in range(sprite_sheet.get_width() // width):
                surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                rect = pygame.Rect(i * width, 0, width, height)
                surface.blit(sprite_sheet, (0, 0), rect)
                sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)



#=========Class=========#
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.appearing = False
        self.disappearing = False


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def start_teleport(self, portal):
        self.disappearing = True
        self.appearing = False
        self.animation_count = 0
        self.teleport_target = (portal.target_x, portal.target_y)

        portal.mask = None

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        
        if self.disappearing:
            self.animation_count += 1
            if self.animation_count >= 21:
                self.disappearing = False
                self.rect.topleft = self.teleport_target
                self.animation_count = 0
                self.appearing = True
        elif self.appearing:
            self.animation_count += 1
            if self.animation_count >= 21:
                self.appearing = False
                self.animation_count = 0

        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.disappearing:
            sprite_sheet = "disappearing"
        elif self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        if self.disappearing:
            sprite_index = min(self.animation_count // self.ANIMATION_DELAY, len(sprites) - 1)
        else:
            sprite_index = (self.animation_count //
                            self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None, frames=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0


class Coin(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "coin")
        self.coin = load_sprite_sheets("Items", "Coins", width, height)
        self.animation_name = "coin"
        self.image = self.coin[self.animation_name][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def loop(self):
        sprites = self.coin[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0


class Portal(Object):
    ANIMATION_DELAY = 6

    def __init__(self, x, y, width, height, target_x, target_y, flip_horizontal=False):
        super().__init__(x, y, width, height, "portal")
        self.portal = load_sprite_sheets("Items", "Portals", width, height, False, 8)
        self.image = self.portal["idle"][0]
        self.animation_count = 0
        self.animation_name = "idle"
        self.target_x = target_x
        self.target_y = target_y
        self.flip_horizontal = flip_horizontal

        self.collision_rect = pygame.Rect(
            x + 20,
            y + 10,
            width - 40,
            height - 20
        )
        

    def appear(self):
        self.animation_name = "appear"

    def disappear(self):
        self.animation_name = "disappear"

    def loop(self):
        sprites = self.portal[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0



#=======Function========#
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, score):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    shadow = PIXEL_FONT.render("COINS: " + str(score), False, (COLOR_BLACK))
    window.blit(shadow, (12, 12))

    score_text = PIXEL_FONT.render("COINS: " + str(score), False, (COLOR_WHITE))
    window.blit(score_text, (10, 10))

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if obj.name != "coin":
            if player.rect.colliderect(obj.rect):
                if dy > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                elif dy < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()

                collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    collided_object = None
    for obj in objects:
        if player.rect.colliderect(obj.rect):
            collided_object = obj
            break

    player.move(-dx, 0)
    return collided_object


def handle_move(player, objects, portal1, portal2):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not collide_left:
        player.move_left(PLAYER_VEL)
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj:
            if obj.name  == "fire":
                player.make_hit()
            elif obj.name == "portal" and not player.disappearing:
                player.start_teleport(obj)


def collect_coins(player, objects):
    to_remove = []
    collected = 0

    for obj in objects:
        if getattr(obj, "name", None) == "coin" and getattr(obj, "mask", None) and getattr(player, "mask", None):
            if pygame.sprite.collide_mask(player, obj):
                to_remove.append(obj)
                collected += 1
    
    for obj in to_remove:
        try:
            objects.remove(obj)
        except ValueError:
            pass

    return collected


def generate_world(width, height, block_size):
    player = Player(20, 600, 50, 50)


    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    coins = [Coin(400, HEIGHT - block_size * 3 - 64, 16, 16),
             Coin(700, HEIGHT - block_size * 2 - 80, 16, 16)]
    
    portal1 = Portal(450, HEIGHT - block_size * 2 - 30, 60, 80, 800, HEIGHT - block_size * 5, flip_horizontal=True)
    portal2 = Portal(650, HEIGHT - block_size * 5 - 30, 60, 80, 375, HEIGHT - block_size * 2)

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    
    vertical_blocks = [Block(block_size*6, HEIGHT - block_size*n, block_size) for n in range(2, 10)]
    additional_objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
                          Block(block_size * 3, HEIGHT - block_size * 4, block_size), 
                          Block(block_size * 7, HEIGHT - block_size * 4, block_size),
                          Block(block_size * 8, HEIGHT - block_size * 4, block_size),
                          Block(block_size * 12, HEIGHT - block_size * 3, block_size), fire]
    objects = vertical_blocks + additional_objects + coins + [portal1, portal2]

    return player, objects, portal1, portal2


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player, objects, portal1, portal2 = generate_world(WIDTH, HEIGHT, block_size)
    offset_x = 0
    scroll_area_width = 400
    score = 0

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        for obj in objects:
            if hasattr(obj, "loop"):
                obj.loop()

        handle_move(player, objects, portal1, portal2)
        score += collect_coins(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, score)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)