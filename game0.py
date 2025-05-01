import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Create screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Asteroids")

# Player
player_img = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.polygon(player_img, (200, 200, 200), [(16, 0), (32, 32), (16, 24), (0, 32)])
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_angle = 0
player_dx = 0
player_dy = 0
player_acceleration = 0.05
player_max_speed = 4
player_rotation_speed = 3
player_lives = 3
player_invincible = False
player_invincible_timer = 0

# Bullets
bullet_img = pygame.Surface((4, 4))
bullet_img.fill((255, 255, 255))
bullets = []
bullet_speed = 10
fire_rate = 250
last_shot_time = 0

# Asteroids
asteroid_images = []
asteroid_sizes = [80, 40, 20]
for size in asteroid_sizes:
    img = pygame.Surface((size, size), pygame.SRCALPHA)
    points = [(size // 2 + size // 2 * math.cos(2 * math.pi * i / 8),
               size // 2 + size // 2 * math.sin(2 * math.pi * i / 8)) for i in range(8)]
    pygame.draw.polygon(img, (150, 150, 150), points, 2)
    asteroid_images.append(img)
asteroids = []

# Game variables
score = 0
level = 1
game_over = False
game_started = False
clock = pygame.time.Clock()

# Functions
def create_asteroids(num):
    for _ in range(num):
        size_idx = 0
        size = asteroid_sizes[size_idx]
        while True:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            if math.hypot(x - player_x, y - player_y) > 150:
                break
        speed = random.uniform(1, 2)
        angle = random.uniform(0, 2 * math.pi)
        asteroids.append({
            'x': x, 'y': y,
            'dx': speed * math.cos(angle),
            'dy': speed * math.sin(angle),
            'size_idx': size_idx, 'size': size,
            'angle': 0, 'spin': random.uniform(-0.05, 0.05)
        })

def draw_player():
    if player_invincible and pygame.time.get_ticks() % 200 < 100:
        return
    rotated_player = pygame.transform.rotate(player_img, -player_angle)
    rect = rotated_player.get_rect(center=(player_x, player_y))
    screen.blit(rotated_player, rect.topleft)

def draw_bullets():
    for bullet in bullets:
        screen.blit(bullet_img, (bullet['x'] - 2, bullet['y'] - 2))

def draw_asteroids():
    for asteroid in asteroids:
        img = asteroid_images[asteroid['size_idx']]
        rotated_img = pygame.transform.rotate(img, asteroid['angle'])
        rect = rotated_img.get_rect(center=(asteroid['x'], asteroid['y']))
        screen.blit(rotated_img, rect.topleft)

def draw_score():
    font = pygame.font.Font(None, 36)
    screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Lives: {player_lives}", True, (255, 255, 255)), (10, 50))
    screen.blit(font.render(f"Level: {level}", True, (255, 255, 255)), (10, 90))

def draw_game_over():
    font = pygame.font.Font(None, 72)
    screen.blit(font.render("GAME OVER", True, (255, 0, 0)), (WIDTH // 2 - 140, HEIGHT // 2 - 50))
    font = pygame.font.Font(None, 36)
    screen.blit(font.render(f"Final Score: {score}", True, (255, 255, 255)), (WIDTH // 2 - 70, HEIGHT // 2 + 20))
    screen.blit(font.render("Press Space to Play Again", True, (255, 255, 255)), (WIDTH // 2 - 140, HEIGHT // 2 + 70))

def draw_start_screen():
    font = pygame.font.Font(None, 72)
    screen.blit(font.render("ASTEROIDS", True, (255, 255, 255)), (WIDTH // 2 - 140, HEIGHT // 3))
    font = pygame.font.Font(None, 36)
    screen.blit(font.render("Press Space to Start", True, (255, 255, 255)), (WIDTH // 2 - 110, HEIGHT // 2))

def check_collisions():
    global score, player_lives, player_invincible, player_invincible_timer, game_over
    global player_x, player_y, player_dx, player_dy
    if not player_invincible:
        for asteroid in asteroids:
            if math.hypot(player_x - asteroid['x'], player_y - asteroid['y']) < asteroid['size'] / 2 + 10:
                player_lives -= 1
                if player_lives <= 0:
                    game_over = True
                else:
                    player_invincible = True
                    player_invincible_timer = pygame.time.get_ticks()
                    player_x = WIDTH // 2
                    player_y = HEIGHT // 2
                    player_dx = 0
                    player_dy = 0
                break
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            if math.hypot(bullet['x'] - asteroid['x'], bullet['y'] - asteroid['y']) < asteroid['size'] / 2:
                bullets.remove(bullet)
                size_idx = asteroid['size_idx']
                if size_idx < 2:
                    for _ in range(2):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(1.5, 3)
                        asteroids.append({
                            'x': asteroid['x'], 'y': asteroid['y'],
                            'dx': speed * math.cos(angle),
                            'dy': speed * math.sin(angle),
                            'size_idx': size_idx + 1,
                            'size': asteroid_sizes[size_idx + 1],
                            'angle': 0, 'spin': random.uniform(-0.1, 0.1)
                        })
                score += [20, 50, 100][size_idx]
                asteroids.remove(asteroid)
                break

def reset_game():
    global player_x, player_y, player_angle, player_dx, player_dy, player_lives
    global player_invincible, player_invincible_timer, bullets, asteroids
    global score, level, game_over, game_started
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player_angle = 0
    player_dx = 0
    player_dy = 0
    player_lives = 3
    player_invincible = False
    player_invincible_timer = 0
    bullets = []
    asteroids = []
    score = 0
    level = 1
    game_over = False
    game_started = True
    create_asteroids(level + 2)

# Game Loop
running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if game_over or not game_started:
                reset_game()
            elif game_started and not game_over:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time > fire_rate:
                    rad_angle = math.radians(90 - player_angle)
                    bullets.append({
                        'x': player_x + 20 * math.cos(rad_angle),
                        'y': player_y - 20 * math.sin(rad_angle),
                        'dx': bullet_speed * math.cos(rad_angle),
                        'dy': -bullet_speed * math.sin(rad_angle),
                        'lifetime': 60
                    })
                    last_shot_time = current_time

    if not game_started:
        draw_start_screen()
    elif game_over:
        draw_game_over()
    else:
        if player_invincible and pygame.time.get_ticks() - player_invincible_timer > 3000:
            player_invincible = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_angle += player_rotation_speed
        if keys[pygame.K_RIGHT]:
            player_angle -= player_rotation_speed
        rad_angle = math.radians(90 - player_angle)
        if keys[pygame.K_UP]:
            player_dx += player_acceleration * math.cos(rad_angle)
            player_dy -= player_acceleration * math.sin(rad_angle)
        speed = math.hypot(player_dx, player_dy)
        if speed > player_max_speed:
            player_dx = player_dx / speed * player_max_speed
            player_dy = player_dy / speed * player_max_speed
        player_x += player_dx
        player_y += player_dy
        player_x %= WIDTH
        player_y %= HEIGHT

        for bullet in bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            bullet['lifetime'] -= 1
            bullet['x'] %= WIDTH
            bullet['y'] %= HEIGHT
            if bullet['lifetime'] <= 0:
                bullets.remove(bullet)

        for asteroid in asteroids:
            asteroid['x'] += asteroid['dx']
            asteroid['y'] += asteroid['dy']
            asteroid['angle'] += asteroid['spin']
            asteroid['x'] %= WIDTH
            asteroid['y'] %= HEIGHT

        check_collisions()
        if not asteroids:
            level += 1
            create_asteroids(level + 2)

        draw_player()
        draw_bullets()
        draw_asteroids()
        draw_score()

    pygame.display.update()
    clock.tick(60)

pygame.quit()