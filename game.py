import pygame
import math
import random
from pygame import mixer

# Initialize pygame
pygame.init()

# Create screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Title and Icon
pygame.display.set_caption("Retro Asteroids")
icon = pygame.Surface((32, 32))
icon.fill((255, 255, 255))
pygame.draw.polygon(icon, (200, 200, 200), [(16, 0), (32, 32), (0, 32)])
pygame.display.set_icon(icon)

# Sound effects
mixer.init()
laser_sound = None
explosion_sound = None
try:
    laser_sound = mixer.Sound('laser.wav')
    explosion_sound = mixer.Sound('explosion.wav')
except:
    print("Sound files not found. Game will run without sound.")

# Static starfield (fixed stars instead of random each frame)
stars = []
for i in range(50):
    stars.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'brightness': random.randint(40, 100)
    })

# Player
player_img = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.polygon(player_img, (200, 200, 200), [(16, 0), (32, 32), (16, 24), (0, 32)])
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_angle = 0
player_speed = 0
player_rotation_speed = 3  # Reduced from 4 for smoother rotation
player_acceleration = 0.05  # Reduced from 0.1 for more gradual acceleration
player_max_speed = 4  # Reduced from 5
player_deceleration = 0.01  # New friction/drag factor
player_dx = 0
player_dy = 0
player_lives = 3
player_invincible = False
player_invincible_timer = 0

# Bullets
bullet_img = pygame.Surface((4, 4))
bullet_img.fill((255, 255, 255))
bullets = []
bullet_speed = 10
fire_rate = 250  # milliseconds between shots
last_shot_time = 0

# Asteroids
asteroid_images = []
for size in [80, 40, 20]:
    img = pygame.Surface((size, size), pygame.SRCALPHA)
    num_points = random.randint(6, 10)
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        radius = size // 2 * (0.8 + 0.4 * random.random())
        x = size // 2 + radius * math.cos(angle)
        y = size // 2 + radius * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(img, (150, 150, 150), points, 2)
    asteroid_images.append(img)

asteroid_sizes = [80, 40, 20]
asteroids = []

# Particle effects
particles = []

# Game variables
score = 0
level = 1
game_over = False
game_paused = False
game_started = False
last_spawn_time = 0
spawn_interval = 3000  # milliseconds between asteroid spawns


# Game functions
def create_asteroids(num):
    for _ in range(num):
        size_idx = 0  # Start with large asteroids
        size = asteroid_sizes[size_idx]

        # Make sure asteroid doesn't spawn too close to player
        while True:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            if math.hypot(x - player_x, y - player_y) > 150:
                break

        speed = random.uniform(1, 2)
        angle = random.uniform(0, 2 * math.pi)
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)
        spin = random.uniform(-0.05, 0.05)

        asteroids.append({
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'size_idx': size_idx,
            'size': size,
            'angle': 0,
            'spin': spin
        })


def draw_player():
    if player_invincible and pygame.time.get_ticks() % 200 < 100:
        return  # Blink effect when invincible

    rotated_player = pygame.transform.rotate(player_img, -player_angle)
    new_rect = rotated_player.get_rect(center=(player_x, player_y))
    screen.blit(rotated_player, new_rect.topleft)


def draw_bullets():
    for bullet in bullets:
        screen.blit(bullet_img, (bullet['x'] - 2, bullet['y'] - 2))


def draw_asteroids():
    for asteroid in asteroids:
        size_idx = asteroid['size_idx']
        img = asteroid_images[size_idx]
        rotated_img = pygame.transform.rotate(img, asteroid['angle'])
        new_rect = rotated_img.get_rect(center=(asteroid['x'], asteroid['y']))
        screen.blit(rotated_img, new_rect.topleft)


def draw_particles():
    for particle in particles:
        alpha = int(particle['life'] * 255)
        pygame.draw.circle(screen, (255, 255, 255, alpha),
                           (int(particle['x']), int(particle['y'])),
                           int(particle['size']))


def draw_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 50))

    level_text = font.render(f"Level: {level}", True, (255, 255, 255))
    screen.blit(level_text, (10, 90))


def draw_game_over():
    font = pygame.font.Font(None, 72)
    text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

    font = pygame.font.Font(None, 36)
    text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 20))

    text = font.render("Press Space to Play Again", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 70))


def draw_start_screen():
    font = pygame.font.Font(None, 72)
    text = font.render("ASTEROIDS", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

    font = pygame.font.Font(None, 36)
    text = font.render("Press Space to Start", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    font = pygame.font.Font(None, 24)
    controls = [
        "Controls:",
        "Arrow keys to move",
        "Space to shoot",
        "P to pause",
        "ESC to quit"
    ]

    y_offset = HEIGHT * 2 // 3
    for line in controls:
        text = font.render(line, True, (200, 200, 200))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 30


def draw_pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, 72)
    text = font.render("PAUSED", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

    font = pygame.font.Font(None, 36)
    text = font.render("Press P to Resume", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 20))


def check_collisions():
    global score, player_lives, player_invincible, player_invincible_timer, game_over
    global player_x, player_y, player_dx, player_dy, player_speed

    # Check player-asteroid collision
    if not player_invincible:
        for asteroid in asteroids:
            distance = math.hypot(player_x - asteroid['x'], player_y - asteroid['y'])
            if distance < asteroid['size'] / 2 + 10:  # Player hit by asteroid
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
                    player_speed = 0
                break

    # Check bullet-asteroid collisions
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            distance = math.hypot(bullet['x'] - asteroid['x'], bullet['y'] - asteroid['y'])
            if distance < asteroid['size'] / 2:
                bullets.remove(bullet)

                # Create particles
                for _ in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1, 3)
                    particles.append({
                        'x': asteroid['x'],
                        'y': asteroid['y'],
                        'dx': speed * math.cos(angle),
                        'dy': speed * math.sin(angle),
                        'size': random.uniform(1, 3),
                        'life': 1.0
                    })

                # Split asteroid
                size_idx = asteroid['size_idx']
                if size_idx < 2:  # Not the smallest size
                    for _ in range(2):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(1.5, 3)
                        new_idx = size_idx + 1
                        new_size = asteroid_sizes[new_idx]

                        asteroids.append({
                            'x': asteroid['x'],
                            'y': asteroid['y'],
                            'dx': speed * math.cos(angle),
                            'dy': speed * math.sin(angle),
                            'size_idx': new_idx,
                            'size': new_size,
                            'angle': random.uniform(0, 360),
                            'spin': random.uniform(-0.1, 0.1)
                        })

                # Increase score based on asteroid size
                if size_idx == 0:  # Large asteroid
                    score += 20
                elif size_idx == 1:  # Medium asteroid
                    score += 50
                else:  # Small asteroid
                    score += 100

                if explosion_sound:
                    explosion_sound.play()

                asteroids.remove(asteroid)
                break


def reset_game():
    global player_x, player_y, player_angle, player_speed, player_dx, player_dy
    global player_lives, player_invincible, player_invincible_timer
    global bullets, asteroids, particles, score, level, game_over, game_started
    global stars

    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player_angle = 0
    player_speed = 0
    player_dx = 0
    player_dy = 0
    player_lives = 3
    player_invincible = False
    player_invincible_timer = 0

    # Generate new static starfield
    stars.clear()
    for i in range(50):
        stars.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'brightness': random.randint(40, 100)
        })

    bullets = []
    asteroids = []
    particles = []
    score = 0
    level = 1
    game_over = False
    game_started = True

    create_asteroids(level + 2)


# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    # Set background
    screen.fill((0, 0, 0))

    # Draw static starfield (much less distracting than random each frame)
    for star in stars:
        pygame.draw.circle(screen, (star['brightness'], star['brightness'], star['brightness']),
                           (star['x'], star['y']), 1)

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_p:
                game_paused = not game_paused

            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                elif not game_started:
                    reset_game()
                elif not game_paused:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_shot_time > fire_rate:
                        # Create new bullet - FIXED DIRECTION FROM NOSE
                        rad_angle = math.radians(90 - player_angle)  # Convert to proper coordinate system
                        bullet_x = player_x + 20 * math.cos(rad_angle)  # Start at the nose of the ship
                        bullet_y = player_y - 20 * math.sin(rad_angle)  # Negative because y increases downward

                        bullets.append({
                            'x': bullet_x,
                            'y': bullet_y,
                            'dx': bullet_speed * math.cos(rad_angle),
                            'dy': -bullet_speed * math.sin(rad_angle),
                            'lifetime': 60  # frames (about 1 second)
                        })
                        last_shot_time = current_time
                        if laser_sound:
                            laser_sound.play()

    if not game_started:
        draw_start_screen()
    elif game_over:
        draw_game_over()
    else:
        # Game logic when not paused
        if not game_paused:
            # Check player invincibility
            if player_invincible and pygame.time.get_ticks() - player_invincible_timer > 3000:
                player_invincible = False

            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_angle += player_rotation_speed
            if keys[pygame.K_RIGHT]:
                player_angle -= player_rotation_speed

            # Convert player angle to radians for movement calculations
            rad_angle = math.radians(90 - player_angle)  # Fixed angle calculation

            if keys[pygame.K_UP]:
                player_dx += player_acceleration * math.cos(rad_angle)
                player_dy -= player_acceleration * math.sin(rad_angle)  # Negative because y increases downward

                # Add thruster particles - FIXED DIRECTION FROM BACK
                if random.random() < 0.3:
                    # Calculate position at back of ship (opposite of nose)
                    back_x = player_x - 15 * math.cos(rad_angle)
                    back_y = player_y + 15 * math.sin(rad_angle)

                    particles.append({
                        'x': back_x,
                        'y': back_y,
                        'dx': -player_dx * 0.5 - random.uniform(0.5, 1.5) * math.cos(rad_angle),
                        'dy': -player_dy * 0.5 + random.uniform(0.5, 1.5) * math.sin(rad_angle),
                        'size': random.uniform(1, 3),
                        'life': random.uniform(0.5, 1)
                    })

            # Limit player speed
            speed = math.hypot(player_dx, player_dy)
            if speed > player_max_speed:
                player_dx = player_dx / speed * player_max_speed
                player_dy = player_dy / speed * player_max_speed

            # Apply deceleration (friction/drag) for smoother movement
            if not keys[pygame.K_UP]:
                # Only apply drag when not thrusting
                player_dx *= (1 - player_deceleration)
                player_dy *= (1 - player_deceleration)

            # Update player position with smoother movement
            player_x += player_dx
            player_y += player_dy

            # Screen wrapping for player
            if player_x < 0:
                player_x = WIDTH
            elif player_x > WIDTH:
                player_x = 0
            if player_y < 0:
                player_y = HEIGHT
            elif player_y > HEIGHT:
                player_y = 0

            # Update bullets
            for bullet in bullets[:]:
                bullet['x'] += bullet['dx']
                bullet['y'] += bullet['dy']
                bullet['lifetime'] -= 1

                # Screen wrapping for bullets
                if bullet['x'] < 0:
                    bullet['x'] = WIDTH
                elif bullet['x'] > WIDTH:
                    bullet['x'] = 0
                if bullet['y'] < 0:
                    bullet['y'] = HEIGHT
                elif bullet['y'] > HEIGHT:
                    bullet['y'] = 0

                # Remove bullets that have expired
                if bullet['lifetime'] <= 0:
                    bullets.remove(bullet)

            # Update asteroids
            for asteroid in asteroids:
                asteroid['x'] += asteroid['dx']
                asteroid['y'] += asteroid['dy']
                asteroid['angle'] += asteroid['spin']

                # Screen wrapping for asteroids
                if asteroid['x'] < -50:
                    asteroid['x'] = WIDTH + 50
                elif asteroid['x'] > WIDTH + 50:
                    asteroid['x'] = -50
                if asteroid['y'] < -50:
                    asteroid['y'] = HEIGHT + 50
                elif asteroid['y'] > HEIGHT + 50:
                    asteroid['y'] = -50

            # Update particles
            for particle in particles[:]:
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
                particle['life'] -= 0.02

                # Remove expired particles
                if particle['life'] <= 0:
                    particles.remove(particle)

            # Check collisions
            check_collisions()

            # Spawn new asteroids over time
            current_time = pygame.time.get_ticks()
            if current_time - last_spawn_time > spawn_interval and len(asteroids) < level * 3 + 5:
                # Spawn a new asteroid from edge
                side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
                if side == 0:
                    x = random.randint(0, WIDTH)
                    y = -50
                elif side == 1:
                    x = WIDTH + 50
                    y = random.randint(0, HEIGHT)
                elif side == 2:
                    x = random.randint(0, WIDTH)
                    y = HEIGHT + 50
                else:
                    x = -50
                    y = random.randint(0, HEIGHT)

                size_idx = random.randint(0, 2)
                size = asteroid_sizes[size_idx]

                # Direction towards center with some randomness
                center_x = WIDTH // 2 + random.randint(-100, 100)
                center_y = HEIGHT // 2 + random.randint(-100, 100)

                angle = math.atan2(center_y - y, center_x - x)
                speed = random.uniform(1, 2)

                asteroids.append({
                    'x': x,
                    'y': y,
                    'dx': speed * math.cos(angle),
                    'dy': speed * math.sin(angle),
                    'size_idx': size_idx,
                    'size': size,
                    'angle': 0,
                    'spin': random.uniform(-0.05, 0.05)
                })

                last_spawn_time = current_time

            # Level progression
            if len(asteroids) == 0:
                level += 1
                create_asteroids(level + 2)

        # Draw game elements
        draw_player()
        draw_bullets()
        draw_asteroids()
        draw_particles()
        draw_score()

        if game_paused:
            draw_pause_screen()

    # Update screen
    pygame.display.update()
    clock.tick(60)

pygame.quit()