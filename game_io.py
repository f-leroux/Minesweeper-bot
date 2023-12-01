import pyautogui
import time
import pygetwindow as gw
import numpy as np
import os

UNREVEALED_SQUARE_COLORS = [(150, 206, 80, 255), (158, 213, 86, 255)]
REVEALED_SQUARE_COLORS = [(226, 188, 152, 255), (211, 177, 145, 255)]
ONE_COLOR = (15, 101, 198, 255)
TWO_COLOR = (44, 132, 60, 255)
THREE_COLOR = (208, 44, 46, 255)
FOUR_COLOR = (114, 9, 147, 255)
FIVE_COLOR = (255, 135, 40, 255)
SQUARE_CENTERS = None
GAME_REGION = None

# Function to check if the correct window is in the foreground
def is_correct_window_foreground(window_title="Google Chrome"):
    return window_title in gw.getActiveWindow().title()

def take_screenshot(return_array=False):
    # Wait until the correct window is active
    window_title = "Google Chrome"
    while not is_correct_window_foreground(window_title):
        time.sleep(0.5)  # Sleep for a bit before checking again

    screenshot = pyautogui.screenshot()
    if return_array:
        return np.array(screenshot).swapaxes(0, 1)
    screenshot = screenshot.load()
    return screenshot

# Function to check if the pixel matches the target colors
def is_target_color(SCREENSHOT, x, y):
    pixel_color = np.array(SCREENSHOT[x, y])
    return min(abs(pixel_color - np.array(UNREVEALED_SQUARE_COLORS[0])).sum(),
                abs(pixel_color - np.array(UNREVEALED_SQUARE_COLORS[1])).sum()) < 15

def find_game_region(screenshot):
    screen_width, screen_height = pyautogui.size()

    start_x = screen_width // 2
    start_y = screen_height // 2

    # Find the bounds of the game region
    def find_bound(direction, start_pos):
        x, y = start_pos
        while 0 <= x < screen_width and 0 <= y < screen_height:
            if not is_target_color(screenshot, x, y):
                break
            if direction == 'up': y -= 1
            elif direction == 'down': y += 1
            elif direction == 'left': x -= 1
            elif direction == 'right': x += 1
        return x, y

    # Find bounds
    left_bound = find_bound('left', (start_x, start_y))[0] + 1
    right_bound = find_bound('right', (start_x, start_y))[0] - 1
    top_bound = find_bound('up', (start_x, start_y))[1] + 1
    bottom_bound = find_bound('down', (start_x, start_y))[1] - 1

    global GAME_REGION
    # Return the coordinates of the game region
    GAME_REGION = (left_bound, top_bound, right_bound - left_bound, bottom_bound - top_bound)



def get_square_coordinates(screenshot):
    # Start from the top-left corner of the game region
    start_x, start_y = GAME_REGION[0]+2, GAME_REGION[1]+2
    starting_color = screenshot[start_x, start_y]
    assert starting_color in UNREVEALED_SQUARE_COLORS
    starting_color_index = UNREVEALED_SQUARE_COLORS.index(starting_color)
    width, height = GAME_REGION[2], GAME_REGION[3]

    # Find vertical boundaries
    def find_vertical_boundaries(x, start_y, height, starting_color_index):
        current_color_index = starting_color_index
        y_boundaries = [start_y]
        for y in range(start_y + 1, start_y + height):
            if screenshot[x, y] == UNREVEALED_SQUARE_COLORS[(current_color_index + 1) % 2]:
                current_color_index = (current_color_index + 1) % 2
                y_boundaries.append(y)
        y_boundaries.append(start_y + height)  # Add the bottom boundary
        return y_boundaries

    # Find horizontal boundaries
    def find_horizontal_boundaries(start_x, y, width, starting_color_index):
        current_color_index = starting_color_index
        x_boundaries = [start_x]
        for x in range(start_x + 1, start_x + width):
            if screenshot[x, y] == UNREVEALED_SQUARE_COLORS[(current_color_index + 1) % 2]:
                current_color_index = (current_color_index + 1) % 2
                x_boundaries.append(x)
        x_boundaries.append(start_x + width)  # Add the right boundary
        return x_boundaries

    # Get all the square boundaries
    y_boundaries = find_vertical_boundaries(start_x, start_y, height, starting_color_index)
    x_boundaries = find_horizontal_boundaries(start_x, start_y, width, starting_color_index)

    # Calculate the center points of squares
    global SQUARE_CENTERS
    SQUARE_CENTERS = np.zeros((len(x_boundaries) - 1, len(y_boundaries) - 1, 2), dtype=int)
    for y in range(len(y_boundaries) - 1):
        for x in range(len(x_boundaries) - 1):
            center_x = (x_boundaries[x] + x_boundaries[x + 1]) // 2
            center_y = (y_boundaries[y] + y_boundaries[y + 1]) // 2
            SQUARE_CENTERS[x, y] = (center_x, center_y)

    # Return the function to get the center, and the number of squares horizontally and vertically
    num_squares_x = len(x_boundaries) - 1
    num_squares_y = len(y_boundaries) - 1
    return num_squares_x, num_squares_y


def click_square(grid_x, grid_y):
    assert SQUARE_CENTERS is not None, "You must call init_game() before calling click_square()"
    center_x, center_y = SQUARE_CENTERS[grid_x, grid_y]
    pyautogui.moveTo(center_x, center_y)
    pyautogui.leftClick()


def init_game():
    screenshot = take_screenshot()
    # Get the game region coordinates
    find_game_region(screenshot)
    print(f"The game region is at: {GAME_REGION}")

    # Get the function to find the center of a square and the number of squares
    num_squares_x, num_squares_y = get_square_coordinates(screenshot)
    print(f"There are {num_squares_x} squares horizontally and {num_squares_y} squares vertically.")
    revealed_squares = np.zeros((num_squares_x, num_squares_y), dtype=bool)
    mines = np.zeros((num_squares_x, num_squares_y), dtype=bool)
    numbers = np.zeros((num_squares_x, num_squares_y), dtype=int)
    return revealed_squares, numbers, mines

def get_square_region(grid_x, grid_y, num_squares_x, num_squares_y, margin=5):
    # Get the coordinates of the square
    center_x, center_y = SQUARE_CENTERS[grid_x, grid_y]
    square_width = GAME_REGION[2] // num_squares_x
    square_height = GAME_REGION[3] // num_squares_y
    left = center_x - square_width // 2
    top = center_y - square_height // 2
    return (left + margin, top + margin, square_width - margin, square_height - margin)

def contains_color(image, color):
    return np.any(np.all(image == color, axis=-1))

def get_square_type(square_image):
    number, revealed = 0, False
    if contains_color(square_image, np.array(ONE_COLOR)):
        number = 1
        revealed = True
    elif contains_color(square_image, np.array(TWO_COLOR)):
        number = 2
        revealed = True
    elif contains_color(square_image, np.array(THREE_COLOR)):
        number = 3
        revealed = True
    elif contains_color(square_image, np.array(FOUR_COLOR)):
        number = 4
        revealed = True
    elif contains_color(square_image, np.array(FIVE_COLOR)):
        number = 5
        revealed = True
    elif contains_color(square_image, np.array(REVEALED_SQUARE_COLORS[0])) or contains_color(square_image, np.array(REVEALED_SQUARE_COLORS[1])): 
        revealed = True
    return number, revealed
    
    

def update_game_state(revealed_squares, numbers):
    assert GAME_REGION is not None, "You must call init_game() before calling get_game_state()"
    assert SQUARE_CENTERS is not None, "You must call init_game() before calling get_game_state()"
    num_squares_x, num_squares_y = revealed_squares.shape 

    os.makedirs('region_images', exist_ok=True)
    screenshot = take_screenshot(return_array=True)
    for x in range(num_squares_x):
        for y in range(num_squares_y):
            if revealed_squares[x, y]:
                continue
            left, top, square_width, square_height = get_square_region(x, y, num_squares_x, num_squares_y)
            square_image = screenshot[left:left + square_width, top:top + square_height]
            number, revealed = get_square_type(square_image)
            revealed_squares[x, y] = revealed
            numbers[x, y] = number
    return revealed_squares, numbers


