import random
import math
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pygame

import numpy as np
import threading

animals = []
food = []
frame_interval = 16.67


class Animal:
    def __init__(self, id, age, size, speed, sight, position, yaw, saturation):
        self.id = id
        self.age = age
        self.size = size
        self.speed = speed
        self.sight = sight
        self.position = position
        self.yaw = yaw
        self.target_food = None  # Track the food target if within sight
        self.saturation = saturation

    def __str__(self):
        return f"{self.id}({self.age}), {self.position}"


class Food:
    def __init__(self, id, nutrition, position):
        self.id = id
        self.nutrition = nutrition
        self.position = position

    def __str__(self):
        return f"{self.id}({self.nutrition})"


def move(animal):
    actual_speed = animal.speed / 100  # Actual speed is half of the speed attribute

    if animal.target_food:
        food_pos = animal.target_food.position
        angle_to_food = math.atan2(food_pos[1] - animal.position[1], food_pos[0] - animal.position[0])
        animal.yaw = math.degrees(angle_to_food)

    yaw = math.radians(animal.yaw)  # Convert yaw to radians for trigonometric functions
    dx = actual_speed * math.cos(yaw)
    dy = actual_speed * math.sin(yaw)
    animal.position[0] += dx
    animal.position[1] += dy

    # Optional: wrap-around movement if the animal goes beyond the grid boundaries
    if animal.position[0] > 100:
        animal.position[0] = -100
    elif animal.position[0] < -100:
        animal.position[0] = 100

    if animal.position[1] > 100:
        animal.position[1] = -100
    elif animal.position[1] < -100:
        animal.position[1] = 100

    # Check if the animal is close enough to eat the food
    if animal.target_food and np.linalg.norm(np.array(animal.position) - np.array(animal.target_food.position)) < 3:
        animal.saturation = 100  # Increase saturation to full
        food.remove(animal.target_food)  # Remove the food from the environment
        for animal in animals:
            animal.target_food = None


def checkforfood(animal):
    for food_item in food:
        distance = np.linalg.norm(np.array(animal.position) - np.array(food_item.position))
        if distance <= animal.sight:
            animal.target_food = food_item
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
    t1 = threading.Thread(checksaturation())
    for i in range(10):
        animal = Animal(i + 1, 0, 10, random.randint(1, 20), 20, createposition(), generateyaw(), 50)
        animals.append(animal)

    for animal in animals:
        print(animal)

    for i in range(20):
        tempfood = Food(i + 1, 100, createposition())
        food.append(tempfood)


def checksaturation():
    for animal in animals:
        if animal.saturation < 0:
            animals.remove(animal)
        else:
            animal.saturation = - 1
    time.sleep(1)


def createmap():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-100, 100)
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

    def init():
        animal_scatter.set_offsets(np.empty((0, 2)))  # Correctly shaped empty array
        for line in sight_lines:
            line.set_data([], [])
        return [animal_scatter] + sight_lines

    def update(frame):
        print("Frame:", frame)
        for _ in range(frame):
            for animal in animals:
                checkforfood(animal)
                move(animal)
                print("Animal:", animal.id, "Position:", animal.position, "Speed:", animal.speed)

            animal_positions = [animal.position for animal in animals]
            if animal_positions:
                animal_x, animal_y = zip(*animal_positions)
                animal_scatter.set_offsets(list(zip(animal_x, animal_y)))
            else:
                animal_scatter.set_offsets(np.empty((0, 2)))

            plot_food_positions()  # Update food positions after potential consumption

            for i, animal in enumerate(animals):
                x0, y0 = animal.position
                yaw = math.radians(animal.yaw)
                x1 = x0 + animal.sight * math.cos(yaw)
                y1 = y0 + animal.sight * math.sin(yaw)
                sight_lines[i].set_data([x0, x1], [y0, y1])

        return [animal_scatter] + sight_lines

    ani = animation.FuncAnimation(fig, update, frames=100, init_func=init, blit=False, interval=16.67)

    plt.legend()
    plt.show()


# Initialise animals and food
initialise()

# Create the map to show real-time movement
createmap()
