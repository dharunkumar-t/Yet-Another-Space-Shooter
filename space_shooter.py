import pygame
import random
import os

pygame.init()

# screen
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Yet Another Space Shooter")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 60)


# images
def load_image(filename, width, height):
    try:
        img = pygame.image.load(filename)
        img = pygame.transform.scale(img, (width, height))
        return img
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        pygame.quit()
        exit()


# sounds
def load_sound(filename):
    try:
        sound = pygame.mixer.Sound(filename)
        return sound
    except pygame.error as e:
        print(f"Error loading sound {filename}: {e}")
        pygame.quit()
        exit()


# Player
player_img = load_image('player_ship.png', 45, 45)
player_width = 45
player_height = 45
player_x = (screen_width - player_width) / 2
player_y = screen_height - player_height - 10
player_speed = 7

# Enemies
enemies = []
enemy_img = load_image('enemy_ship.png', 40, 40)
enemy_speed = 3
enemy_spawn_rate = 60

# Bullets
bullets = []
bullet_img = load_image('bullet.png', 20, 20)
bullet_width = 20
bullet_height = 20
bullet_speed = 10

# Enemy bullets
enemy_bullets = []
enemy_bullet_img = load_image('bullet.png', 20, 20)  # Reusing bullet image for enemy bullets
enemy_bullet_speed = 5
enemy_shoot_rate = 90

# Game variables
score = 0
high_score = 0
health = 3

if os.path.exists('high_score.txt'):
    with open('high_score.txt', 'r') as file:
        high_score = int(file.read())

# Sounds
bullet_sound = load_sound('laser.wav')
explosion_sound = load_sound('explosion.wav')

game_over_img = load_image('game_over.png', 900, 900)

def player(x, y):
    screen.blit(player_img, (x, y))


def create_enemy():
    new_enemy = {
        "x": random.randint(0, screen_width - enemy_img.get_width()),
        "y": 0,
        "speed": enemy_speed
    }
    enemies.append(new_enemy)


def draw_enemy(x, y):
    screen.blit(enemy_img, (x, y))


def create_bullet(x, y):
    new_bullet = {"x": x, "y": y, "speed": bullet_speed}
    bullets.append(new_bullet)


def draw_bullet(x, y):
    screen.blit(bullet_img, (x, y))


def create_enemy_bullet(x, y):
    new_enemy_bullet = {"x": x, "y": y, "speed": enemy_bullet_speed}
    enemy_bullets.append(new_enemy_bullet)


def draw_enemy_bullet(x, y):
    screen.blit(enemy_bullet_img, (x, y))


def collision(x1, y1, x2, y2, w1, h1, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def display_score(score, high_score):
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))
    high_score_text = font.render("High Score: " + str(high_score), True, WHITE)
    screen.blit(high_score_text, (10, 40))


def display_health(health):
    health_text = font.render("Health: " + str(health), True, WHITE)
    screen.blit(health_text, (screen_width - 100, 10))


def game_over():
    screen.blit(game_over_img, (
    screen_width // 2 - game_over_img.get_width() // 2, screen_height // 2 - game_over_img.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()
    exit()



running = True
clock = pygame.time.Clock()
spawn_timer = 0
shoot_timer = 0

# background image
bg_img = load_image('bg.png', 375, 375)

while running:
    screen.fill(BLACK)

    # background image center
    bg_rect = bg_img.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(bg_img, bg_rect.topleft)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_sound.play()
                create_bullet(player_x + player_width / 2 - bullet_width / 2, player_y)

        # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed


    if player_x < 0:
        player_x = 0
    elif player_x > screen_width - player_width:
        player_x = screen_width - player_width
    if player_y < 0:
        player_y = 0
    elif player_y > screen_height - player_height:
        player_y = screen_height - player_height


    spawn_timer += 1
    if spawn_timer == enemy_spawn_rate:
        create_enemy()
        spawn_timer = 0

    # Enemy shooting
    shoot_timer += 1
    if shoot_timer == enemy_shoot_rate:
        for enemy in enemies:
            create_enemy_bullet(enemy["x"] + enemy_img.get_width() / 2 - enemy_bullet_img.get_width() / 2,
                                enemy["y"] + enemy_img.get_height())
        shoot_timer = 0

    for enemy in enemies:
        enemy["y"] += enemy["speed"]
        draw_enemy(enemy["x"], enemy["y"])

        # enemy hit player
        if collision(player_x, player_y, enemy["x"], enemy["y"], player_width, player_height, enemy_img.get_width(),
                     enemy_img.get_height()):
            explosion_sound.play()
            enemies.remove(enemy)
            health -= 1
            if health == 0:
                game_over()

        # enemy hit bullets
        for bullet in bullets:
            if collision(bullet["x"], bullet["y"], enemy["x"], enemy["y"], bullet_width, bullet_height,
                         enemy_img.get_width(), enemy_img.get_height()):
                explosion_sound.play()
                score += 10
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

        # remove enemies
        if enemy["y"] > screen_height:
            enemies.remove(enemy)

    for bullet in bullets:
        bullet["y"] -= bullet["speed"]
        draw_bullet(bullet["x"], bullet["y"])

        # remove bullets
        if bullet["y"] < 0:
            bullets.remove(bullet)

    for enemy_bullet in enemy_bullets:
        enemy_bullet["y"] += enemy_bullet["speed"]
        draw_enemy_bullet(enemy_bullet["x"], enemy_bullet["y"])

        # enemy bullet hit player
        if collision(player_x, player_y, enemy_bullet["x"], enemy_bullet["y"], player_width, player_height,
                     enemy_bullet_img.get_width(), enemy_bullet_img.get_height()):
            explosion_sound.play()
            enemy_bullets.remove(enemy_bullet)
            health -= 1
            if health == 0:
                game_over()

        if enemy_bullet["y"] > screen_height:
            enemy_bullets.remove(enemy_bullet)

    # score and health
    display_score(score, high_score)
    display_health(health)

    player(player_x, player_y)

    pygame.display.update()
    clock.tick(60)

pygame.quit()


