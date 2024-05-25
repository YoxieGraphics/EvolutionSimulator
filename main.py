import math
import random

import matplotlib.pyplot as plt
import numpy as np
import pygame

reproductionReadyAnimals = []
animalIDs = []
pygame.init()
animals = []
food = []
frame_interval = 16.67
scaling_factor = 3  # Adjust as needed
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Animal Simulation")
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PINK = (255, 153, 255)
BLACK = (0, 0, 0)


class Animal:
    def __init__(self, id, age, size, speed, sight, position, yaw, saturation, lifespan):
        self.id = id
        self.age = age
        self.size = size
        self.speed = speed
        self.sight = sight
        self.position = position
        self.yaw = yaw
        self.target_food = None  # Track the food target if within sight
        self.target_animal = None
        self.saturation = saturation
        self.lifespan = lifespan

    def __str__(self):
        return f"{self.id}({self.age}), {self.position}"


class Food:
    def __init__(self, id, nutrition, position):
        self.id = id
        self.nutrition = nutrition
        self.position = position

    def __str__(self):
        return f"{self.id}({self.nutrition})"


def get_offspring_stats(animal, target_animal):
    def get_offspring_id(animals):
        for animal in animals:
            animalIDs.append(animal.id)
        newID = max(animalIDs) + 1
        return newID
    avgSize = (animal.size + target_animal.size)/2
    newSize = random.uniform(avgSize-5, avgSize+10)

    avgSpeed = (animal.speed + target_animal.speed)/2
    newSpeed = random.uniform(avgSpeed-5, avgSpeed+10)

    avgSight = (animal.sight + target_animal.sight) / 2
    newSight = random.uniform(avgSight - 5, avgSight + 10)

    avgLifespan = (animal.lifespan + target_animal.lifespan)/2
    newLifespan = random.uniform(avgLifespan - 5, avgSight+ 20)
    return Animal(id=get_offspring_id(animals),
                  age=0,
                  size=newSize,
                  speed=newSpeed,
                  sight=newSight,
                  position=[0, 0],
                  yaw=90,
                  saturation=50,
                  lifespan=newLifespan)


def move(animal):
    actual_speed = animal.speed / 100
    if animal.target_animal:
        animal_pos = animal.target_animal.position
        angle_to_animal = math.atan2(animal_pos[1] - animal.position[1], animal_pos[0] - animal.position[0])

        animal.yaw = math.degrees(angle_to_animal)
    elif animal.target_food:
        food_pos = animal.target_food.position
        angle_to_food = math.atan2(food_pos[1] - animal.position[1], food_pos[0] - animal.position[0])
        animal.yaw = math.degrees(angle_to_food)

    yaw = math.radians(animal.yaw)  # Convert yaw to radians for trigonometric functions
    dx = actual_speed * math.cos(yaw)
    dy = actual_speed * math.sin(yaw)
    animal.position[0] += dx
    animal.position[1] += dy

    # Optional: wrap-around movement if the animal goes beyond the grid boundaries
    if animal.position[0] > 200:
        animal.position[0] = -200
    elif animal.position[0] < -200:
        animal.position[0] = 200

    if animal.position[1] > 100:
        animal.position[1] = -100
    elif animal.position[1] < -100:
        animal.position[1] = 100

    # Check if the animal is close enough to eat the food
    if animal.target_animal and np.linalg.norm(np.array(animal.position) - np.array(animal.target_animal.position)) < 3:
        offspring = get_offspring_stats(animal, animal.target_animal)
        animals.append(offspring)
        print(f"Welcome, {offspring.id}!")
        animal.target_animal = None
        animal.saturation -= 75
    elif animal.target_food and np.linalg.norm(np.array(animal.position) - np.array(animal.target_food.position)) < 3:
        animal.saturation += animal.target_food.nutrition  # Increase saturation to full
        food.remove(animal.target_food)  # Remove the food from the environment
        for animal in animals:
            animal.target_food = None


def checkforfood(animal):
    for food_item in food:
        distance = np.linalg.norm(np.array(animal.position) - np.array(food_item.position))
        if distance <= animal.sight:
            animal.target_food = food_item
            break


def reproduction_checks(animal):
    for other_animal in animals:
        if other_animal is not animal:
            # Check if the other animal is within sight
            distance = np.linalg.norm(np.array(animal.position) - np.array(other_animal.position))
            if distance <= animal.sight and animal in reproductionReadyAnimals and other_animal in reproductionReadyAnimals:
                # Target the other animal
                animal.target_animal = other_animal
                break


def createposition():
    xaxis = random.randint(-100, 100)
    yaxis = random.randint(-100, 100)
    position = [xaxis, yaxis]
    return position


def generateyaw():
    yaw = random.randint(0, 360)
    return yaw


def initialise():
    for i in range(10):
        animal = Animal(i + 1, 0, 10, random.randint(1, 20), 20, createposition(), generateyaw(), 50, random.randint(90,150))
        animals.append(animal)

    for i in range(20):
        tempfood = Food(i + 1, 100, createposition())
        food.append(tempfood)


def createmap():
    fig, ax = plt.subplots(figsize=(50, 20))
    ax.set_xlim(-200, 200)
    ax.set_ylim(-100, 100)
    ax.set_title("Map of Animals and Food")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.grid(True)
    animal_scatter = ax.scatter([], [], c='blue', label='Animals', marker='o')
    food_scatter = ax.scatter([], [], c='green', label='Food', marker='x')
    sight_lines = [ax.plot([], [], c='red')[0] for _ in animals]

    # Plot initial food positions
    def plot_food_positions():
        food_positions = [item.position for item in food]
        if food_positions:
            food_x, food_y = zip(*food_positions)
            food_scatter.set_offsets(list(zip(food_x, food_y)))
        else:
            food_scatter.set_offsets(np.empty((0, 2)))

    plot_food_positions()

    def chooseanimalcolor(animal):
            if animal.saturation < 25:
                if animal in reproductionReadyAnimals:
                    reproductionReadyAnimals.remove(animal)
                return RED
            elif animal.saturation > 150:
                if animal not in reproductionReadyAnimals:
                    print(f"Animal with ID {animal.id} is ready for reproduction!")
                    reproductionReadyAnimals.append(animal)
                return PINK
            else:
                if animal in reproductionReadyAnimals:
                    reproductionReadyAnimals.remove(animal)
                return BLUE

    font = pygame.font.Font(None, 20)  # Define font for the stats text
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update animal positions and check for food
        for animal in animals:
            if animal.saturation < 0 or animal.age > 100:
                animals.remove(animal)
            else:
                animal.saturation -= 0.025
                animal.age += 0.025
            checkforfood(animal)
            reproduction_checks(animal)
            move(animal)

        # Clear the screen
        screen.fill(WHITE)

        # Draw animals and their stats
        for animal in animals:
            # Scale the position of the animal
            scaled_position = (int(animal.position[0] * scaling_factor + screen_width / 2),
                               int(animal.position[1] * scaling_factor + screen_height / 2))
            pygame.draw.circle(screen, chooseanimalcolor(animal), scaled_position, animal.size / 2)
            if animal.sight > 0:
                # Calculate the radius of the circle based on the animal's sight
                radius = int(animal.sight * scaling_factor)
                # Draw the circle with transparency (alpha value)
                pygame.draw.circle(screen, (0, 0, 255, 100), scaled_position, radius, 1)

            # Display animal stats
            stats_text = font.render(f"ID: {animal.id}, Age: {round(animal.age)}, Saturation: {round(animal.saturation)}", True, BLACK)
            screen.blit(stats_text, (scaled_position[0] + 10, scaled_position[1] + 10))  # Adjust text position
            changeYaw = random.randint(1, 150)
            if changeYaw == 1:
                animal.yaw = random.randint(1, 360)
        spawnFood = random.randint(1, 50)
        if spawnFood == 1:
            for i in range(1):
                tempfood = Food(i + 1, 100, createposition())
                food.append(tempfood)


        # Draw food
        for food_item in food:
            # Scale the position of the food
            scaled_position = (int(food_item.position[0] * scaling_factor + screen_width / 2),
                               int(food_item.position[1] * scaling_factor + screen_height / 2))
            pygame.draw.rect(screen, GREEN, (scaled_position[0], scaled_position[1], 5, 5))

        # Update the display
        pygame.display.flip()

        if len(food) < 2:
            for i in range(20):
                tempfood = Food(i + 1, 100, createposition())
                food.append(tempfood)


        # Cap the frame rate
        clock.tick(1000 / frame_interval)

initialise()

# Create the map to show real-time movement
createmap()
