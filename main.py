import math
import random
import pygame
import numpy as np
from matplotlib import pyplot as plt

animals = []
food = []
animalIDs = []
reproductionReadyAnimals = []

pygame.init()
frame_interval = 3 #Default is 16.67
scaling_factor = 3
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Animal Simulation")
WHITE = (250, 250, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PINK = (255, 153, 255)
BLACK = (0, 0, 0)


class Animal:
    def __init__(self, animal_id, age, size, speed, sight, position, yaw,
                 saturation, lifespan, is_predator, refractory_period):
        self.id = animal_id
        self.age = age
        self.size = size
        self.speed = speed
        self.sight = sight
        self.position = position
        self.yaw = yaw
        self.saturation = saturation
        self.lifespan = lifespan
        self.is_predator = is_predator
        self.refractory_period = refractory_period
        self.target_animal = None
        self.target_food = None

    def __str__(self):
        return f"{self.id}({self.age}), {self.position}"


class Food:
    def __init__(self, food_id, nutrition, position):
        self.id = food_id
        self.nutrition = nutrition
        self.position = position

    def __str__(self):
        return f"{self.id}({self.nutrition})"


def generate_yaw():
    yaw = random.randint(0, 360)
    return yaw


def create_position():
    x_axis = random.randint(-100, 100)
    yaxis = random.randint(-100, 100)
    position = [x_axis, yaxis]
    return position


def initialise():
    for i in range(10):
        animal = Animal(i + 1, 0, 10, random.randint(1, 20), 20, create_position(), generate_yaw(), 50,
                        random.randint(90, 150), False, 0)
        animals.append(animal)

    for i in range(20):
        temp_food = Food(i + 1, 100, create_position())
        food.append(temp_food)


def check_for_food(animal):
    if animal.saturation > 200:  # Assuming 150 for reproduction readiness + 50
        animal.target_food = None
        return
    for food_item in food:
        distance = np.linalg.norm(np.array(animal.position) - np.array(food_item.position))
        if distance <= animal.sight:
            animal.target_food = food_item
            break



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

    yaw = math.radians(animal.yaw)
    dx = actual_speed * math.cos(yaw)
    dy = actual_speed * math.sin(yaw)
    animal.position[0] += dx
    animal.position[1] += dy

    if animal.position[0] > 200:
        animal.position[0] = -200
    elif animal.position[0] < -200:
        animal.position[0] = 200

    if animal.position[1] > 100:
        animal.position[1] = -100
    elif animal.position[1] < -100:
        animal.position[1] = 100

    if animal.target_animal and np.linalg.norm(np.array(animal.position) - np.array(animal.target_animal.position)) < 3:
        animal.saturation = 75
        offspring = get_offspring_stats(animal, animal.target_animal)
        animal.target_animal = None
        if offspring is not None:
            animals.append(offspring)

    elif animal.target_food and np.linalg.norm(np.array(animal.position) - np.array(animal.target_food.position)) < 3:
        animal.saturation += animal.target_food.nutrition
        food.remove(animal.target_food)
        for a in animals:
            a.target_food = None

    # Saturation reduction based on speed
    if animal.speed != 0:
        animal.saturation -= 0.025 * (1 / (animal.speed/1.7))
    else:
        animal.saturation -= 0.025





def get_offspring_stats(animal, target_animal):
    if animal.refractory_period <= 0 and target_animal.refractory_period <= 0:
        def get_offspring_id(local_animals):
            for local_animal in local_animals:
                animalIDs.append(local_animal.id)

            new_id = max(animalIDs) + 1
            return new_id

        avg_size = (animal.size + target_animal.size) / 2
        new_size = random.uniform(avg_size - 5, avg_size + 10)

        avg_speed = (animal.speed + target_animal.speed) / 2
        new_speed = random.uniform(avg_speed - 5, avg_speed + 10)

        avg_sight = (animal.sight + target_animal.sight) / 2
        new_sight = random.uniform(avg_sight - 5, avg_sight + 10)

        avg_lifespan = (animal.lifespan + target_animal.lifespan) / 2
        new_lifespan = random.uniform(avg_lifespan - 5, avg_lifespan + 20)

        is_predator = random.choice([True, False])
        animal.refractory_period = 30
        target_animal.refractory_period = 30

        offspring = Animal(animal_id=get_offspring_id(animals),
                           age=0,
                           size=new_size,
                           speed=new_speed,
                           sight=new_sight,
                           position=[0, 0],
                           yaw=90,
                           saturation=50,
                           lifespan=new_lifespan,
                           is_predator=is_predator,
                           refractory_period=0)
        print(f"New offspring created with ID: {offspring.id}")
        return offspring
    return None

def reproduction_checks(animal):
    if animal.refractory_period <= 0:
        for other_animal in animals:
            if other_animal is not None and other_animal is not animal:
                if other_animal.refractory_period <= 0:
                    distance = np.linalg.norm(np.array(animal.position) - np.array(other_animal.position))
                    if distance <= animal.sight and animal in reproductionReadyAnimals:
                        animal.target_animal = other_animal
                        break


def create_map():
    fig, ax = plt.subplots(figsize=(50, 20))
    ax.set_xlim(-200, 200)
    ax.set_ylim(-100, 100)
    ax.set_title("Map of Animals and Food")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.grid(True)
    food_scatter = ax.scatter([], [], c='green', label='Food', marker='x')

    def plot_food_positions():
        food_positions = [item.position for item in food]
        if food_positions:
            food_x, food_y = zip(*food_positions)
            food_scatter.set_offsets(list(zip(food_x, food_y)))
        else:
            food_scatter.set_offsets(np.empty((0, 2)))

    plot_food_positions()

    def choose_animal_color(target_animal):
        if target_animal.saturation < 25:
            if target_animal in reproductionReadyAnimals:
                reproductionReadyAnimals.remove(target_animal)
            return RED
        elif target_animal.saturation > 150:
            if target_animal not in reproductionReadyAnimals:
                reproductionReadyAnimals.append(target_animal)
            return PINK
        else:
            if target_animal in reproductionReadyAnimals:
                reproductionReadyAnimals.remove(target_animal)
            return BLUE

    font = pygame.font.Font(None, 20)
    clock = pygame.time.Clock()
    running = True
    step = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        global animals
        animals = [animal for animal in animals if animal is not None]

        for animal in animals:
            if animal.saturation < 0 or animal.age > 100:
                print(f"Removing animal {animal.id} due to low saturation or old age")
                animals.remove(animal)
            else:
                animal.saturation -= 0.025
                animal.age += 0.025
                animal.refractory_period -= 0.025
            check_for_food(animal)
            reproduction_checks(animal)
            move(animal)

        screen.fill(WHITE)

        for animal in animals:
            scaled_position = (int(animal.position[0] * scaling_factor + screen_width / 2),
                               int(animal.position[1] * scaling_factor + screen_height / 2))
            pygame.draw.circle(screen, choose_animal_color(animal), scaled_position, int(animal.size / 2))

            # Detailed stats text
            stats_text = (f"ID: {animal.id}\n"
                          f"Age: {round(animal.age, 2)}\n"
                          f"Saturation: {round(animal.saturation, 2)}\n"
                          f"Speed: {round(animal.speed, 2)}\n"
                          f"Sight: {round(animal.sight, 2)}")
            y_offset = 0
            for line in stats_text.split('\n'):
                text_surface = font.render(line, True, BLACK)
                screen.blit(text_surface, (scaled_position[0] + 10, scaled_position[1] + 10 + y_offset))
                y_offset += 15  # Adjust the line height as needed

        spawn_food = random.randint(1, 50)
        if spawn_food == 1:
            for i in range(1):
                temp_food = Food(i + 1, 100, create_position())
                food.append(temp_food)

        for food_item in food:
            scaled_position = (int(food_item.position[0] * scaling_factor + screen_width / 2),
                               int(food_item.position[1] * scaling_factor + screen_height / 2))
            pygame.draw.rect(screen, GREEN, (scaled_position[0], scaled_position[1], 5, 5))

        pygame.display.flip()

        if len(food) < 2:
            for i in range(20):
                temp_food = Food(i + 1, 100, create_position())
                food.append(temp_food)

        clock.tick(1000 / frame_interval)
        step += 1

    pygame.quit()

initialise()
create_map()
