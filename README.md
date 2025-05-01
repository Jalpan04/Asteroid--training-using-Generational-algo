Asteroids Game with AI Agents
A Pygame implementation of the classic Asteroids game, enhanced with AI agents trained using neural networks and a genetic algorithm (GA). The AI learns to navigate and survive in the game by evolving over generations, optimizing its ability to avoid asteroids and shoot them down.
Project Overview
This project builds a retro-style Asteroids game where a spaceship navigates a 2D space, avoiding and destroying asteroids. The game features:

A player-controlled spaceship (manual mode in game_base.py) or AI-controlled spaceship (AI mode in learning.py).
Asteroids of varying sizes that split into smaller pieces when shot.
A scoring system, lives, and level progression (in manual mode).
AI agents trained using a genetic algorithm and neural networks to control the spaceship autonomously.

The AI mode focuses on training agents to survive as long as possible by dodging asteroids and shooting them strategically. The training process leverages evolutionary principles to improve agent performance over generations.
Installation
Prerequisites

Python 3.8+
Pygame (for game rendering and mechanics)

Setup

Clone the repository:git clone <repository-url>
cd asteroids-ai


Install dependencies:pip install -r requirements.txt


Run the game:
Manual mode: python game_base.py
AI training mode: python learning.py



Game Mechanics

Player (Spaceship):
Controlled via keyboard (manual mode) or AI (AI mode). nails can rotate left/right, thrust forward, and shoot bullets.
Has a maximum speed and acceleration for realistic movement.
Wraps around screen edges (toroidal space).


Asteroids:
Spawn with random positions, velocities, and sizes (large, medium, small).
Split into smaller asteroids when hit by bullets.
Wrap around screen edges.


Bullets:
Fired by the spaceship with a cooldown (fire rate).
Have a limited lifetime and wrap around screen edges.


Scoring:
Points awarded for destroying asteroids (20 for large, 50 for medium, 100 for small).
In AI mode, fitness is based on survival time and score.



AI Training: Neural Networks and Genetic Algorithm
The AI agents are trained using a combination of neural networks (NN) and a genetic algorithm (GA). The goal is to evolve agents that maximize survival time and score by navigating and shooting effectively.
Development Journey
Initially, I created a manual version of the Asteroids game where players control the spaceship using keyboard inputs. This served as the foundation, with core mechanics like asteroid spawning, collision detection, and scoring. The game worked well, but I wanted to explore AI-driven gameplay to see if a neural network could learn to play autonomously.
The first challenge was designing an AI that could interpret the game environment. I implemented a neural network with a simple input layer capturing the spaceship’s velocity, the distance to the nearest asteroid, and the relative angle to it. The network output four actions: rotate left, rotate right, thrust, and shoot. A genetic algorithm was used to evolve a population of agents, each defined by their network weights. Fitness was based on the score, but I noticed agents weren’t surviving long because they lacked incentives for evasion.
To address this, I modified the fitness function to include survival time alongside the score, encouraging agents to avoid collisions. I also introduced periodic asteroid spawning instead of level-based spawning to create a continuous challenge. However, the AI struggled with precise navigation, often failing to align with asteroids for effective shooting.
Next, I expanded the input layer to include the relative velocity of the nearest asteroid, providing richer context about the game state. I also added heuristic overrides to guide the AI when asteroids were close, such as forcing rotation toward the asteroid or disabling shooting if misaligned. These changes improved performance, but the game wasn’t optimized for all environments.
To solve this, I integrated asyncio to make the game loop more flexible, ensuring smooth execution across different platforms. The final AI implementation in learning.py combines a robust neural network, genetic algorithm, and heuristics, resulting in agents that effectively dodge and shoot asteroids while evolving over generations.
Neural Network Architecture
Each agent uses a feedforward neural network:

Input Layer: 6 neurons:
Normalized player velocity (player_dx / player_max_speed, player_dy / player_max_speed).
Normalized distance to the nearest asteroid (min_dist / 300).
Normalized relative angle to the nearest asteroid (nearest_angle / π).
Relative velocity of the nearest asteroid (rel_dx, rel_dy).


Hidden Layer: 10 neurons with sigmoid activation (sigmoid(x) = 1 / (1 + e^(-x))).
Output Layer: 4 neurons (binary actions):
Rotate left (0 or 1).
Rotate right (0 or 1).
Thrust (0 or 1).
Shoot (0 or 1).



The network has:

Weights from input to hidden: 6 × 10 = 60.
Weights from hidden to output: 10 × 4 = 40.
Total weights: 60 + 40 = 100.

The forward pass computes:

Hidden layer: h_i = sigmoid(∑_{j=1}^6 w_{ij} x_j), for i = 1, ..., 10.
Output layer: o_k = sigmoid(∑_{j=1}^{10} w_{jk} h_j), for k = 1, ..., 4.
Actions: a_k = 1 if o_k > 0.5 else 0.

Genetic Algorithm
The GA evolves a population of agents:

Population Size: 20 agents.
Fitness Function: fitness = current_survival_time + 3 × score.
Initialization: Weights are randomly initialized in [-1, 1].
Selection:
Tournament selection: Pick 5 agents from the top 20, select the best.


Crossover:
Each weight is chosen from parent1 or parent2 (50% chance).


Mutation:
5% chance per weight to add a random value in [-0.2, 0.2], clipped to [-1, 1].


Elitism:
Top 10 agents are retained; the rest are generated via crossover and mutation.



Enhanced Decision-Making
Heuristics improve AI performance:

Rotation: Force rotation toward the nearest asteroid if it’s close (min_dist / 300 < 0.5) and misaligned (|nearest_angle| > 0.2π).
Shooting: Disable shooting if the asteroid is not aligned (|nearest_angle| > 30°).
Thrusting: Enable thrust if the asteroid is close (min_dist / 300 < 0.4) and the ship is slow (speed < 1.5).

Training Dynamics

Game State: Captures velocity, distance, angle, and relative velocity of the nearest asteroid.
Fitness Pressure: Rewards survival and asteroid destruction.
Convergence: Best survival time increases as weights optimize.
Visualization: A red line connects the ship to the nearest asteroid.

Running the Game

Manual Mode (game_base.py):
Use arrow keys to rotate and thrust, spacebar to shoot.
Progress through levels by clearing asteroids.


AI Mode (learning.py):
Watch AI agents play autonomously.
Observe generation, agent number, survival time, and best survival time.



Project Structure

game_base.py: Manual Asteroids game.
learning.py: Final AI-driven implementation.
requirements.txt: Lists dependencies (pygame).

Future Improvements

Add complex neural network architectures.
Incorporate multi-asteroid awareness.
Experiment with varied fitness functions.
Implement a player vs. AI mode.

License
MIT License. See LICENSE for details.
