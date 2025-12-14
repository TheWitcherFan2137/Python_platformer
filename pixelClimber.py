import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Pixel Climber")
icon = pygame.image.load("assets/Items/Checkpoints/End/End.png")
pygame.display.set_icon(icon)

WIDTH, HEIGHT = 1200, 800
FPS = 60
PLAYER_VEL = 5

PIXEL_FONT = pygame.font.Font("assets/Fonts/pixel.ttf", 16)
PIXEL_FONT_MEDIUM = pygame.font.Font("assets/Fonts/pixel.ttf", 32)
PIXEL_FONT_LARGE = pygame.font.Font("assets/Fonts/pixel.ttf", 48)

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_LIGHT_GRAY = (200, 200, 200)

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, dir3, width, height, direction=False, frames=None):
    if dir3 is not None:
        path = join("assets", dir1, dir2, dir3)
    else:
        path = join("assets", dir1, dir2)

    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        if frames is not None:
            frame_w = sprite_sheet.get_width() / frames
            for i in range(frames):
                surface = pygame.Surface((int(frame_w), height), pygame.SRCALPHA)
                rect = pygame.Rect(int(i * frame_w), 0, int(frame_w), height)
                surface.blit(sprite_sheet, (0, 0), rect)
                sprites.append(pygame.transform.scale2x(surface))
        else:
            for i in range(sprite_sheet.get_width() // width):
                surface = pygame.Surface((width, height), pygame.SRCALPHA)
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
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", None, 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.sprite = self.SPRITES["idle_right"][0]
        self.rect = self.sprite.get_rect(topleft=(x, y))
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
        self.fade_alpha = 0 

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

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.y_vel *= -0.5

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.disappearing:
            sprite_sheet = "disappearing"
        elif self.appearing:
            sprite_sheet = "appearing"
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
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]

        self.animation_count += 1
        self.update()

    def update(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

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
            self.fade_alpha = min(255, self.fade_alpha + 15)
            self.animation_count += 1
            if self.animation_count >= 21:
                self.disappearing = False
                self.rect.topleft = self.teleport_target
                self.animation_count = 0
                self.appearing = True

        elif self.appearing:
            self.fade_alpha = max(0, self.fade_alpha - 15)
            self.animation_count += 1
            if self.animation_count >= 21:
                self.appearing = False
                self.animation_count = 0
        else:
            self.fade_alpha = 0

        self.update_sprite()


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
    ANIMATION_DELAY = 6

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", None, width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
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
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0


class Coin(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "coin")
        self.coin = load_sprite_sheets("Items", "Coins", None, width, height)
        self.animation_name = "coin"
        self.image = self.coin[self.animation_name][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.animation_count = 0

    def loop(self):
        sprites = self.coin[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0


class Portal(Object):
    ANIMATION_DELAY = 6

    def __init__(self, x, y, width, height, target_x, target_y, flip_horizontal=False):
        super().__init__(x, y, width, height, "portal")
        self.portal = load_sprite_sheets("Items", "Portals", None, width, height, False, 8)
        self.image = self.portal["idle"][0]
        self.animation_count = 0
        self.animation_name = "idle"
        self.target_x = target_x
        self.target_y = target_y
        self.flip_horizontal = flip_horizontal
        self.rect = self.image.get_rect(topleft=(x, y))

        self.collision_rect = pygame.Rect(
            self.rect.centerx - 15,
            self.rect.y + 10,
            30,
            self.rect.height -20
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

        self.collision_rect.center = self.rect.center


class Hearts:
    def __init__(self, x, y, hearts=3):
        self.x = x
        self.y = y
        self.max_hearts = hearts
        self.current_health = hearts * 2
        self.dead = False
        self.sprites = load_sprite_sheets("Menu", "Hearts", None, 32, 32, False, 3)["PixelHeart16"]

    def set_health(self, hp):
        self.current_health = max(0, min(hp, self.max_hearts * 2))

    def draw(self, win):
        for i in range(self.max_hearts):
            heart_x = self.x + i * 40
            heart_value = self.current_health - i * 2

            if heart_value >= 2:
                sprite = self.sprites[0]
            elif heart_value == 1:
                sprite = self.sprites[1]
            else:
                sprite = self.sprites[2]

            win.blit(sprite, (heart_x, self.y))

    def check_death(self):
        if self.current_health <= 0:
            self.dead = True


class Flag(Object):
    ANIMATION_DELAY = 2
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checkpoint")
        self.checkpoint = load_sprite_sheets("Items", "Checkpoints", "Checkpoint", width, height)
        self.image = self.checkpoint["CheckpointNo"][0]
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.animation_count = 0
        self.animation_name = "CheckpointNo"
        self.activated = False

    def finish(self):
        self.animation_name = "Checkpoint"
        self.animation_count = 0
        self.activated = True
    

    def loop(self):
        sprites = self.checkpoint[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        if self.animation_count >= 52:
            self.animation_name = "CheckpointYes"
            self.animation_count = 0
        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0



#=======Function========#
def draw_end_screen(window, background, bg_image, score, message="GAME OVER"):
    go_bg_tiles, go_bg_img = get_background("Gray.png")
    for tile in go_bg_tiles:
        window.blit(go_bg_img, tile)
    
    # Tekst GAME OVER
    message_shadow = PIXEL_FONT_LARGE.render(message, False, COLOR_BLACK)
    message_text = PIXEL_FONT_LARGE.render(message, False, (255, 50, 50))
    message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    window.blit(message_shadow, (message_rect.x + 3, message_rect.y + 3))
    window.blit(message_text, message_rect)
    
    # Wynik
    score_shadow = PIXEL_FONT_MEDIUM.render(f"COINS: {score}", False, COLOR_BLACK)
    score_text = PIXEL_FONT_MEDIUM.render(f"COINS: {score}", False, COLOR_YELLOW)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(score_shadow, (score_rect.x + 2, score_rect.y + 2))
    window.blit(score_text, score_rect)
    
    # Instrukcja
    instruction_shadow = PIXEL_FONT.render("Naciśnij ESC aby wrócić do menu", False, COLOR_BLACK)
    instruction_text = PIXEL_FONT.render("Naciśnij ESC aby wrócić do menu", False, COLOR_WHITE)
    instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    window.blit(instruction_shadow, (instruction_rect.x + 1, instruction_rect.y + 1))
    window.blit(instruction_text, instruction_rect)
    
    pygame.display.update()


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, score, hearts):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    shadow = PIXEL_FONT.render("COINS: " + str(score), False, (COLOR_BLACK))
    window.blit(shadow, (12, 12))

    score_text = PIXEL_FONT.render("COINS: " + str(score), False, (COLOR_WHITE))
    window.blit(score_text, (10, 10))
    
    hearts.draw(window)

    if player.fade_alpha > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(player.fade_alpha)
        window.blit(overlay, (0, 0))


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


def handle_move(player, objects, portal1, portal2, hearts):
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
                if not player.hit:
                    player.make_hit()
                    hearts.set_health(hearts.current_health - 1)
                    hearts.check_death()
            elif obj.name == "portal" and not player.disappearing and not player.appearing:
                    player.start_teleport(obj)
            elif obj.name == "checkpoint":
                if not obj.activated:
                    obj.finish()


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
    
    portal1 = Portal(475, HEIGHT - block_size * 2 - 30, 60, 80, 800, HEIGHT - block_size * 5)
    portal2 = Portal(650, HEIGHT - block_size * 5 - 30, 60, 80, 400, HEIGHT - block_size * 2)

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    
    vertical_blocks = [Block(block_size*6, HEIGHT - block_size*n, block_size) for n in range(2, 10)]
    additional_objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
                          Block(block_size * 3, HEIGHT - block_size * 4, block_size), 
                          Block(block_size * 7, HEIGHT - block_size * 4, block_size),
                          Block(block_size * 8, HEIGHT - block_size * 4, block_size),
                          Block(block_size * 12, HEIGHT - block_size * 3, block_size), fire]
    objects = vertical_blocks + additional_objects + coins + [portal1, portal2]

    flag = Flag(WIDTH * 2 - 100, HEIGHT - (block_size * 1.65) - 64, 64, 64)
    objects.append(flag)


    return player, objects, portal1, portal2


def main_game(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player, objects, portal1, portal2 = generate_world(WIDTH, HEIGHT, block_size)
    offset_x = 0
    scroll_area_width = 400
    score = 0
    game_over = False
    level_completed = False
    show_end_screen = False
    hearts = Hearts(10, 30, 3)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_RETURN:
                        return True
                else:
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w) and player.jump_count < 2:
                        player.jump()
                    if event.key == pygame.K_ESCAPE:
                        return True

        if not game_over and not level_completed:
            player.loop(FPS)
            if player.appearing:
                offset_x = player.rect.x - WIDTH // 2


            for obj in objects:
                if hasattr(obj, "loop"):
                    obj.loop()

            handle_move(player, objects, portal1, portal2, hearts)
            score += collect_coins(player, objects)
            
            if hearts.dead:
                game_over = True
            
            level_completed = False
            for obj in objects:
                if obj.name == "checkpoint" and obj.animation_name == "CheckpointYes":
                    level_completed = True
                    break
            
            draw(window, background, bg_image, player, objects, offset_x, score, hearts)

            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                    (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel
        else:
            if level_completed:
                draw_end_screen(window, background, bg_image, score, message="YOU WIN")
            elif game_over:
                draw_end_screen(window, background, bg_image, score, message="GAME OVER")

    return False


def main_menu(window):
    running = True
    background_tiles, bg_image = get_background("Blue.png")
    clock = pygame.time.Clock()
    selected_option = 0  # 0 = Graj, 1 = Wyjdź

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = 0
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = 1
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected_option == 0:
                        return True  # Start gry
                    else:
                        return False  # Wyjście
                elif event.key == pygame.K_ESCAPE:
                    return False

        # Rysowanie tła
        mm_bg_tiles, mm_bg_img = get_background("Gray.png")
        for tile in mm_bg_tiles:
            window.blit(mm_bg_img, tile)
        
        # Tytuł gry
        title_shadow = PIXEL_FONT_LARGE.render("Pixel Climber", True, COLOR_BLACK)
        title_text = PIXEL_FONT_LARGE.render("Pixel Climber", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        window.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        window.blit(title_text, title_rect)

        # Opcja "GRAJ"
        play_color = COLOR_YELLOW if selected_option == 0 else COLOR_LIGHT_GRAY
        play_text_shadow = PIXEL_FONT_MEDIUM.render("GRAJ", True, COLOR_BLACK)
        play_text = PIXEL_FONT_MEDIUM.render("GRAJ", True, play_color)
        play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        
        # Wskaźnik wyboru dla opcji "GRAJ"
        if selected_option == 0:
            indicator = PIXEL_FONT_MEDIUM.render(">", True, COLOR_YELLOW)
            window.blit(indicator, (play_rect.x - 40, play_rect.y))
        
        window.blit(play_text_shadow, (play_rect.x + 2, play_rect.y + 2))
        window.blit(play_text, play_rect)

        # Opcja "WYJDŹ"
        quit_color = COLOR_YELLOW if selected_option == 1 else COLOR_LIGHT_GRAY
        quit_text_shadow = PIXEL_FONT_MEDIUM.render("WYJDŹ", True, COLOR_BLACK)
        quit_text = PIXEL_FONT_MEDIUM.render("WYJDŹ", True, quit_color)
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        
        # Wskaźnik wyboru dla opcji "WYJDŹ"
        if selected_option == 1:
            indicator = PIXEL_FONT_MEDIUM.render(">", True, COLOR_YELLOW)
            window.blit(indicator, (quit_rect.x - 40, quit_rect.y))
        
        window.blit(quit_text_shadow, (quit_rect.x + 2, quit_rect.y + 2))
        window.blit(quit_text, quit_rect)
        
        # Instrukcja sterowania
        controls = [
            "STEROWANIE:",
            "Strzałki / WASD - ruch",
            "SPACJA / Strzałka w górę - skok",
            "ENTER - wybierz"
        ]
        
        y_offset = HEIGHT // 2 + 180
        for line in controls:
            control_shadow = PIXEL_FONT.render(line, True, COLOR_BLACK)
            control_text = PIXEL_FONT.render(line, True, COLOR_WHITE)
            control_rect = control_text.get_rect(center=(WIDTH // 2, y_offset))
            window.blit(control_shadow, (control_rect.x + 1, control_rect.y + 1))
            window.blit(control_text, control_rect)
            y_offset += 25

        pygame.display.update()


def main(window):
    while True:
        start_game = main_menu(window)
        if not start_game:
            break
        back_to_menu = main_game(window)
        if not back_to_menu:
            break
    pygame.quit()
    quit()



if __name__ == "__main__":
    main(window)