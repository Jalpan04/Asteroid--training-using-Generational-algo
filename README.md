# 🚀 Asteroids Game with Neural Network AI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/pygame-2.0.1+-green.svg)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern implementation of the classic Asteroids arcade game enhanced with artificially intelligent agents trained using neural networks and genetic algorithms. Watch AI pilots evolve from novices to experts as they learn to navigate space, avoid hazards, and destroy asteroids with increasing efficiency.

![Asteroids AI Demo](https://via.placeholder.com/800x400?text=Asteroids+AI+Demo)

## 🔭 Project Overview

This project reimagines the retro-style Asteroids game with a modern twist: AI agents trained to play the game autonomously. The core gameplay involves navigating a spaceship through a field of asteroids while shooting them to score points and avoid collisions.

The AI implementation combines neural networks with evolutionary algorithms to develop agents that learn optimal navigation and shooting strategies through a process mimicking natural selection.

## ✨ Features

### Game Modes
- **Manual Mode**: Classic gameplay with keyboard controls
- **AI Mode**: Watch AI agents navigate and survive autonomously
- **Training Visualization**: Real-time display of neural network decision-making

### AI Technology
- Neural network-driven decision making
- Genetic algorithm for evolutionary learning
- Performance tracking across generations
- Visual representation of AI decision processes

### Game Elements
- Physics-based movement with momentum and inertia
- Asteroid splitting mechanics
- Screen-wrapping (toroidal space)
- Progressive difficulty scaling

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Pygame (for game rendering and mechanics)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/asteroids-ai.git
cd asteroids-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
# For manual gameplay:
python game_base.py

# For AI training mode:
python learning.py
```

## 🎮 Game Mechanics

### Spaceship
- **Control**: Keyboard (manual) or neural network (AI mode)
- **Physics**: Realistic momentum with acceleration/deceleration
- **Movement**: Rotation, thrust, and shooting capabilities
- **Boundaries**: Wraps around screen edges

### Asteroids
- **Variety**: Three size categories (large, medium, small)
- **Behavior**: Split into smaller fragments when shot
- **Generation**: Random initial position, velocity, and rotation
- **Collision**: Destroys ship or splits upon bullet impact

### Scoring System
- **Points**: Large asteroids (20), Medium asteroids (50), Small asteroids (100)
- **AI Fitness**: Combined function of survival time and score

### Difficulty Progression
- **Manual Mode**: Level-based asteroid density increase
- **AI Mode**: Time-based periodic spawning with increasing frequency

## 🧠 Neural Network Architecture

The AI agents utilize a feedforward neural network to process game state information and output control decisions.

### Network Structure

#### Input Layer (6 neurons)
Input features are normalized to ensure efficient learning:

- Player velocity components: $\frac{v_x}{v_{max}}$, $\frac{v_y}{v_{max}}$
- Distance to nearest asteroid: $\frac{d_{min}}{d_{scale}}$ where $d_{scale} = 300$
- Relative angle to nearest asteroid: $\frac{\theta}{π}$
- Relative velocity of nearest asteroid: $v_{rel_x}$, $v_{rel_y}$

#### Hidden Layer (10 neurons)
Each hidden neuron $h_i$ computes:

$$h_i = \sigma\left(\sum_{j=1}^{6} w_{ij} \cdot x_j\right)$$

where $\sigma(z) = \frac{1}{1 + e^{-z}}$ is the sigmoid activation function.

#### Output Layer (4 neurons)
Each output neuron $o_k$ computes:

$$o_k = \sigma\left(\sum_{j=1}^{10} w_{jk} \cdot h_j\right)$$

The four outputs correspond to binary actions:
1. Rotate Left: $a_1 = \begin{cases} 1 & \text{if } o_1 > 0.5 \\ 0 & \text{otherwise} \end{cases}$
2. Rotate Right: $a_2 = \begin{cases} 1 & \text{if } o_2 > 0.5 \\ 0 & \text{otherwise} \end{cases}$
3. Thrust: $a_3 = \begin{cases} 1 & \text{if } o_3 > 0.5 \\ 0 & \text{otherwise} \end{cases}$
4. Shoot: $a_4 = \begin{cases} 1 & \text{if } o_4 > 0.5 \\ 0 & \text{otherwise} \end{cases}$

### Parameter Dimensions
- Input to Hidden: $W_1 \in \mathbb{R}^{6 \times 10}$ (60 weights)
- Hidden to Output: $W_2 \in \mathbb{R}^{10 \times 4}$ (40 weights)
- Total parameters: 100 weights

## 🧬 Genetic Algorithm Implementation

The genetic algorithm evolves the neural network weights across generations to improve performance.

### Core Components

#### Population Management
- **Population Size**: 20 agents per generation
- **Genome Representation**: 100 floating-point weights in range [-1, 1]

#### Fitness Function
The fitness of an agent is calculated as:

$$f = T_{survival} + 3 \cdot S_{points}$$

where $T_{survival}$ is the survival time in seconds and $S_{points}$ is the score from destroying asteroids.

#### Selection Mechanism
Tournament selection with the following process:
1. Select top 20 performing agents
2. Randomly sample 5 agents from this pool
3. Choose the agent with highest fitness as parent

#### Crossover Operation
For each weight in the child network:

$$w_{child, i} = \begin{cases} 
w_{parent1, i} & \text{with probability } 0.5 \\
w_{parent2, i} & \text{with probability } 0.5
\end{cases}$$

#### Mutation Operation
Each weight has a 5% chance of mutation:

$$w'_i = \text{clip}(w_i + \delta, -1, 1)$$

where $\delta \sim \mathcal{U}(-0.2, 0.2)$ is a uniform random value and clip constrains the result to [-1, 1].

#### Elitism Strategy
- Top 10 agents preserved unchanged
- Bottom 10 replaced with offspring from crossover and mutation

## 🏋️ Training Process

### Initialization
1. Generate initial population with random weights
2. Evaluate each agent's fitness in the game environment

### Training Loop
1. Sort population by fitness
2. Implement elitism (preserve top performers)
3. Generate offspring through selection, crossover, and mutation
4. Replace lower-performing agents with offspring
5. Repeat for specified number of generations

### Heuristic Enhancements
To accelerate learning, behavior heuristics are implemented:

- **Rotation Assistance**: If $\frac{d_{min}}{300} < 0.5$ and $|\theta| > 0.2\pi$, force rotation toward asteroid
- **Shooting Regulation**: If $|\theta| > 30°$, disable shooting
- **Thrust Management**: If $\frac{d_{min}}{300} < 0.4$ and $v < 1.5$, enable thrust

These heuristics provide initial guidance while allowing the neural network to develop more sophisticated strategies over time.

### Visualization
During training, the following are displayed:
- Current generation number
- Agent index within population
- Current survival time
- Best survival time achieved
- Visual indicator connecting ship to nearest asteroid

## 📝 Development Journey

### Phase 1: Game Foundation
The project began with implementing a classic Asteroids game with manual controls. This established the core mechanics:
- Physics-based movement
- Collision detection
- Asteroid spawning and splitting
- Scoring system

### Phase 2: Initial AI Implementation
The first AI implementation featured:
- Simple neural network with basic inputs
- Genetic algorithm with fitness based only on score
- Limited environment awareness

**Challenge**: Agents showed poor survival skills as they lacked incentive for evasive maneuvers.

### Phase 3: Enhanced Perception
To improve AI performance:
- Added survival time to fitness function
- Expanded neural inputs to include relative velocity
- Implemented continuous asteroid spawning for consistent challenge

**Challenge**: Agents struggled with precise navigation and shooting alignment.

### Phase 4: Heuristic Guidance
Introduced heuristic overrides to:
- Guide rotation when asteroids are close
- Prevent wasting bullets when misaligned
- Manage thrust based on proximity and velocity

### Phase 5: Performance Optimization
Final improvements included:
- Asyncio integration for consistent execution across platforms
- Optimized rendering for training speed
- Refined genetic algorithm parameters

## 📊 Performance Metrics

### Learning Curve
Typical performance progression across generations:
- **Gen 1-5**: Random movements, average survival < 5 seconds
- **Gen 6-15**: Basic avoidance, survival time 10-20 seconds
- **Gen 16-30**: Coordinated movement and shooting, survival time 30-60 seconds
- **Gen 31+**: Advanced strategies, survival time 60+ seconds

### Evaluation Metrics
- **Survival Time**: Primary measure of agent fitness
- **Score**: Secondary measure of shooting efficiency
- **Generation-to-Competence**: Number of generations to reach 30+ seconds survival

## 🚀 Future Improvements

### Enhanced Neural Network
- Implement convolutional layers for direct screen input
- Add recurrent connections for temporal awareness
- Explore reinforcement learning approaches

### Multi-Asteroid Awareness
- Extend inputs to track multiple nearest asteroids
- Implement attention mechanisms for threat prioritization

### Advanced Training Techniques
- Implement novelty search to encourage exploration
- Add curriculum learning with progressive difficulty
- Explore neuroevolution of augmenting topologies (NEAT)

### Gameplay Extensions
- Player vs. AI competitive mode
- AI difficulty selection based on generation
- Interactive training interface

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

=
