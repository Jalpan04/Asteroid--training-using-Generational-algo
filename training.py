import pygame
import math
import random
import asyncio

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
FPS = 60

# Genetic Algorithm and Neural Network
population_size = 50
input_size = 4  # player_dx, player_dy, asteroid_dist, asteroid_angle
hidden_size = 10
output_size = 4  # rotate_left, rotate_right, thrust, shoot
weights_size = input_size * hidden_size + hidden_size * output_size  # 40 + 40 = 80 weights
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
    # Split weights
    w1 = weights[:input_size * hidden_size]  # 4x10 = 40 weights
    w2 = weights[input_size * hidden_size:]  # 10x4 = 40 weights

    # Input to hidden
    hidden = [0] * hidden_size
    for i in range(hidden_size):
        for j in range(input_size):
            hidden[i] += inputs[j] * w1[i * input_size + j]
        hidden[i] = sigmoid(hidden[i])

    # Hidden to output
    outputs = [0] * output_size
    for i in range(output_size):
        for j in range(hidden_size):
            outputs[i] += hidden[j] * w2[i * hidden_size + j]
        outputs[i] = sigmoid(outputs[i])

    # Convert to binary actions (threshold at 0.5)
    return [1 if o > 0.5 else 0 for o in outputs]


def get_game_state():
    # Find nearest asteroid
    min_dist = float('inf')
    nearest_angle = 0
    player_rad = math.radians(90 - player_angle)
    for asteroid in asteroids:
        dx = asteroid['x'] - player_x
        dy = asteroid['y'] - player_y
        dist = math.hypot(dx, dy)
        if dist < min_dist:
            min_dist = dist
            # Angle from player to asteroid relative to player's facing
            abs_angle = math.atan2(-dy, dx)
            rel_angle = (abs_angle - player_rad) % (2 * math.pi)
            if rel_angle > math.pi:
                rel_angle -= 2 * math.pi
            nearest_angle = rel_angle

    # Normalize inputs
    inputs = [
        player_dx / player_max_speed,  # Normalize velocity
        player_dy / player_max_speed,
        min_dist / 300 if asteroids else 1,  # Normalize distance (max 300)
        nearest_angle / math.pi if asteroids else 0  # Normalize angle
    ]
    return inputs


def evolve_population():
    global population, generation, best_survival_time
    # Sort by fitness (descending)
    population.sort(key=lambda x: x['fitness'], reverse=True)
    # Update best survival time
    best_survival_time = max(best_survival_time, population[0]['fitness'] / FPS)

    # Keep top 10 agents
    new_population = population[:10]

    # Generate 40 offspring
    while len(new_population) < population_size:
        # Select parents (tournament selection)
        tournament = random.sample(population[:20], 5)
        parent1 = max(tournament, key=lambda x: x['fitness'])
        tournament = random.sample(population[:20], 5)
        parent2 = max(tournament, key=lambda x: x['fitness'])

        # Crossover
        child_weights = []
        for w1, w2 in zip(parent1['weights'], parent2['weights']):
            if random.random() < 0.5:
                child_weights.append(w1)
            else:
                child_weights.append(w2)

        # Mutation
        for i in range(len(child_weights)):
            if random.random() < 0.05:
                child_weights[i] += random.uniform(-0.2, 0.2)
                child_weights[i] = max(-1, min(1, child_weights[i]))

        new_population.append({'weights': child_weights, 'fitness': 0})

    population = new_population
    generation += 1


# Game functions (unchanged)
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
    screen.blit(font.render(f"Generation: {generation}", True, (255, 255, 255)), (10, 130))
    screen.blit(font.render(f"Agent: {current_agent_idx + 1}/{population_size}", True, (255, 255, 255)), (10, 170))
    screen.blit(font.render(f"Survival: {current_survival_time / FPS:.1f}s", True, (255, 255, 255)), (10, 210))
    screen.blit(font.render(f"Best Survival: {best_survival_time:.1f}s", True, (255, 255, 255)), (10, 250))


def draw_game_over():
    font = pygame.font.Font(None, 72)
    screen.blit(font.render("GAME OVER", True, (255, 0, 0)), (WIDTH // 2 - 140, HEIGHT // 2 - 50))
    font = pygame.font.Font(None, 36)
    screen.blit(font.render(f"Final Score: {score}", True, (255, 255, 255)), (WIDTH // 2 - 70, HEIGHT // 2 + 20))


def draw_start_screen():
    font = pygame.font.Font(None, 72)
    screen.blit(font.render("ASTEROIDS GA", True, (255, 255, 255)), (WIDTH // 2 - 140, HEIGHT // 3))
    font = pygame.font.Font(None, 36)
    screen.blit(font.render("Training Started", True, (255, 255, 255)), (WIDTH // 2 - 110, HEIGHT // 2))


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
    global score, level, game_over, game_started, current_survival_time
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
    current_survival_time = 0
    create_asteroids(level + 2)


# Initialize population
initialize_population()


async def main():
    global running, game_started, game_over, current_agent_idx, score, current_survival_time
    global player_angle, player_x, player_y, player_dx, player_dy, player_lives
    global player_invincible, player_invincible_timer, bullets, asteroids, level
    global last_shot_time
    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        if not game_started:
            draw_start_screen()
            game_started = True
            reset_game()
        elif game_over:
            # Assign fitness and move to next agent
            population[current_agent_idx]['fitness'] = score
            current_agent_idx += 1
            if current_agent_idx >= population_size:
                evolve_population()
                current_agent_idx = 0
            reset_game()
        else:
            # AI control
            inputs = get_game_state()
            actions = neural_network(inputs, population[current_agent_idx]['weights'])
            rotate_left, rotate_right, thrust, shoot = actions

            # Apply actions
            if rotate_left:
                player_angle += player_rotation_speed
            if rotate_right:
                player_angle -= player_rotation_speed
            rad_angle = math.radians(90 - player_angle)
            if thrust:
                player_dx += player_acceleration * math.cos(rad_angle)
                player_dy -= player_acceleration * math.sin(rad_angle)
            if shoot:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time > fire_rate:
                    bullets.append({
                        'x': player_x + 20 * math.cos(rad_angle),
                        'y': player_y - 20 * math.sin(rad_angle),
                        'dx': bullet_speed * math.cos(rad_angle),
                        'dy': -bullet_speed * math.sin(rad_angle),
                        'lifetime': 60
                    })
                    last_shot_time = current_time

            # Update player
            speed = math.hypot(player_dx, player_dy)
            if speed > player_max_speed:
                player_dx = player_dx / speed * player_max_speed
                player_dy = player_dy / speed * player_max_speed
            player_x += player_dx
            player_y += player_dy
            player_x %= WIDTH
            player_y %= HEIGHT

            # Update bullets
            for bullet in bullets[:]:
                bullet['x'] += bullet['dx']
                bullet['y'] += bullet['dy']
                bullet['lifetime'] -= 1
                bullet['x'] %= WIDTH
                bullet['y'] %= HEIGHT
                if bullet['lifetime'] <= 0:
                    bullets.remove(bullet)

            # Update asteroids
            for asteroid in asteroids:
                asteroid['x'] += asteroid['dx']
                asteroid['y'] += asteroid['dy']
                asteroid['angle'] += asteroid['spin']
                asteroid['x'] %= WIDTH
                asteroid['y'] %= HEIGHT

            # Handle invincibility
            if player_invincible and pygame.time.get_ticks() - player_invincible_timer > 3000:
                player_invincible = False

            # Check collisions
            check_collisions()

            # Advance level
            if not asteroids:
                level += 1
                create_asteroids(level + 2)

            # Increment survival time
            current_survival_time += 1

            # Draw everything
            draw_player()
            draw_bullets()
            draw_asteroids()
            draw_score()

        pygame.display.update()
        await asyncio.sleep(1.0 / FPS)


if __name__ == "__main__":
    asyncio.run(main())

pygame.quit()
