import pygame
import math
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids with GA")

# Player setup
player_img = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.polygon(player_img, (200, 200, 200), [(16, 0), (32, 32), (16, 24), (0, 32)])
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_angle = 0
player_dx = 0
player_dy = 0
player_acceleration = 0.08
player_max_speed = 4
player_rotation_speed = 2
player_lives = 1
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
game_over = False
game_started = False
FPS = 60

# Asteroid spawn
asteroid_spawn_timer = 0
asteroid_spawn_interval = 2000  # milliseconds

# GA + NN
population_size = 20
input_size = 6
hidden_size = 10
output_size = 4
weights_size = input_size * hidden_size + hidden_size * output_size
population = []
current_agent_idx = 0
generation = 1
best_survival_time = 0
current_survival_time = 0

def initialize_population():
    global population
    population = []
    for _ in range(population_size):
        weights = [random.uniform(-1, 1) for _ in range(weights_size)]
        population.append({'weights': weights, 'fitness': 0})

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def neural_network(inputs, weights):
    w1 = weights[:input_size * hidden_size]
    w2 = weights[input_size * hidden_size:]
    hidden = [0] * hidden_size
    for i in range(hidden_size):
        for j in range(input_size):
            hidden[i] += inputs[j] * w1[i * input_size + j]
        hidden[i] = sigmoid(hidden[i])
    outputs = [0] * output_size
    for i in range(output_size):
        for j in range(hidden_size):
            outputs[i] += hidden[j] * w2[i * hidden_size + j]
        outputs[i] = sigmoid(outputs[i])
    return [1 if o > 0.5 else 0 for o in outputs]

def enhanced_get_game_state():
    min_dist = float('inf')
    nearest_angle = 0
    nearest = None
    player_rad = math.radians(90 - player_angle)

    for asteroid in asteroids:
        dx = asteroid['x'] - player_x
        dy = asteroid['y'] - player_y
        dist = math.hypot(dx, dy)
        if dist < min_dist:
            min_dist = dist
            nearest = asteroid
            abs_angle = math.atan2(-dy, dx)
            rel_angle = (abs_angle - player_rad) % (2 * math.pi)
            if rel_angle > math.pi:
                rel_angle -= 2 * math.pi
            nearest_angle = rel_angle

    if nearest:
        rel_dx = (nearest['dx'] - player_dx) / 3.0
        rel_dy = (nearest['dy'] - player_dy) / 3.0
    else:
        min_dist = 300
        nearest_angle = 0
        rel_dx = rel_dy = 0

    return [
        player_dx / player_max_speed,
        player_dy / player_max_speed,
        min_dist / 300,
        nearest_angle / math.pi,
        rel_dx,
        rel_dy
    ]

def evolve_population():
    global population, generation, best_survival_time
    population.sort(key=lambda x: x['fitness'], reverse=True)
    best_survival_time = max(best_survival_time, population[0]['fitness'] / FPS)
    new_population = population[:10]
    while len(new_population) < population_size:
        parent1 = max(random.sample(population[:20], 5), key=lambda x: x['fitness'])
        parent2 = max(random.sample(population[:20], 5), key=lambda x: x['fitness'])
        child_weights = []
        for w1, w2 in zip(parent1['weights'], parent2['weights']):
            child_weights.append(w1 if random.random() < 0.5 else w2)
        for i in range(len(child_weights)):
            if random.random() < 0.05:
                child_weights[i] += random.uniform(-0.2, 0.2)
                child_weights[i] = max(-1, min(1, child_weights[i]))
        new_population.append({'weights': child_weights, 'fitness': 0})
    population = new_population
    generation += 1

def spawn_asteroid():
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
    screen.blit(font.render(f"Generation: {generation}", True, (255, 255, 255)), (10, 50))
    screen.blit(font.render(f"Agent: {current_agent_idx + 1}/{population_size}", True, (255, 255, 255)), (10, 90))
    screen.blit(font.render(f"Survival: {current_survival_time / FPS:.1f}s", True, (255, 255, 255)), (10, 130))
    screen.blit(font.render(f"Best Survival: {best_survival_time:.1f}s", True, (255, 255, 255)), (10, 170))


def reset_game():
    global player_x, player_y, player_angle, player_dx, player_dy, player_lives
    global player_invincible, player_invincible_timer, bullets, asteroids
    global score, game_over, game_started, current_survival_time
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player_angle = 0
    player_dx = 0
    player_dy = 0
    player_lives = 1
    player_invincible = False
    player_invincible_timer = 0
    bullets = []
    asteroids = []
    score = 0
    game_over = False
    game_started = True
    current_survival_time = 0

def check_collisions():
    global score, player_lives, player_invincible, player_invincible_timer, game_over
    if not player_invincible:
        for asteroid in asteroids:
            if math.hypot(player_x - asteroid['x'], player_y - asteroid['y']) < asteroid['size'] / 2 + 10:
                game_over = True
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

def setup():
    initialize_population()

async def update_loop():
    global running, game_started, game_over, current_agent_idx, score, current_survival_time
    global player_angle, player_x, player_y, player_dx, player_dy, player_lives
    global player_invincible, player_invincible_timer, bullets, asteroids, asteroid_spawn_timer
    global last_shot_time

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    if not game_started:
        reset_game()
    elif game_over:
        fitness = current_survival_time + score * 3
        population[current_agent_idx]['fitness'] = fitness
        print(f"Agent {current_agent_idx + 1} fitness: {fitness:.2f}")
        current_agent_idx += 1
        if current_agent_idx >= population_size:
            evolve_population()
            current_agent_idx = 0
        reset_game()
    else:
        inputs = enhanced_get_game_state()
        inputs[3] *= 2  # weight angle more aggressively
        actions = neural_network(inputs, population[current_agent_idx]['weights'])
        rotate_left, rotate_right, thrust, shoot = actions

        if inputs[2] < 0.5:
            if inputs[3] < -0.2:
                rotate_left = 1
                rotate_right = 0
            elif inputs[3] > 0.2:
                rotate_left = 0
                rotate_right = 1
            else:
                rotate_left = rotate_right = 0

        shoot_angle = abs(inputs[3] * math.pi)
        if shoot_angle > math.radians(30):
            shoot = 0

        speed = math.hypot(player_dx, player_dy)
        if inputs[2] < 0.4 and speed < 1.5:
            thrust = 1

        if rotate_left:
            player_angle += player_rotation_speed
        if rotate_right:
            player_angle -= player_rotation_speed

        rad_angle = math.radians(90 - player_angle)
        if thrust:
            player_dx += player_acceleration * math.cos(rad_angle)
            player_dy -= player_acceleration * math.sin(rad_angle)
        if shoot:
            now = pygame.time.get_ticks()
            if now - last_shot_time > fire_rate:
                bullets.append({
                    'x': player_x + 20 * math.cos(rad_angle),
                    'y': player_y - 20 * math.sin(rad_angle),
                    'dx': bullet_speed * math.cos(rad_angle),
                    'dy': -bullet_speed * math.sin(rad_angle),
                    'lifetime': 60
                })
                last_shot_time = now

        player_dx *= 0.99
        player_dy *= 0.99

        speed = math.hypot(player_dx, player_dy)
        if speed > player_max_speed:
            player_dx = player_dx / speed * player_max_speed
            player_dy = player_dy / speed * player_max_speed

        player_x = (player_x + player_dx) % WIDTH
        player_y = (player_y + player_dy) % HEIGHT

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

        now = pygame.time.get_ticks()
        if now - asteroid_spawn_timer > asteroid_spawn_interval:
            spawn_asteroid()
            asteroid_spawn_timer = now

        check_collisions()
        current_survival_time += 1

        draw_player()
        draw_bullets()
        draw_asteroids()
        draw_score()

        if asteroids:
            nearest = min(asteroids, key=lambda a: math.hypot(player_x - a['x'], player_y - a['y']))
            pygame.draw.line(screen, (255, 0, 0), (player_x, player_y), (nearest['x'], nearest['y']), 1)

    pygame.display.update()

async def main():
    global running
    running = True
    setup()
    while running:
        await update_loop()
        await asyncio.sleep(1.0 / FPS)
    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
