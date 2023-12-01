import pyautogui
import time
import pygetwindow as gw
from PIL import Image
import numpy as np

UNREVEALED_SQUARE_COLORS = [(150, 206, 80, 255), (158, 213, 86, 255)]
SQUARE_CENTERS = None

# Function to check if the correct window is in the foreground
def is_correct_window_foreground(window_title="Google Chrome"):
    return window_title in gw.getActiveWindow().title()


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

    # Return the coordinates of the game region
    return (left_bound, top_bound, right_bound - left_bound, bottom_bound - top_bound)



def get_square_coordinates(game_region, screenshot):
    # Start from the top-left corner of the game region
    start_x, start_y = game_region[0]+2, game_region[1]+2
    starting_color = screenshot[start_x, start_y]
    assert starting_color in UNREVEALED_SQUARE_COLORS
    starting_color_index = UNREVEALED_SQUARE_COLORS.index(starting_color)
    width, height = game_region[2], game_region[3]

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
    # Wait until the correct window is active
    window_title = "Google Chrome"
    while not is_correct_window_foreground(window_title):
        time.sleep(0.5)  # Sleep for a bit before checking again

    screenshot = pyautogui.screenshot()
    screenshot = screenshot.load()

    # Get the game region coordinates
    game_region = find_game_region(screenshot)
    print(f"The game region is at: {game_region}")

    # Get the function to find the center of a square and the number of squares
    num_squares_x, num_squares_y = get_square_coordinates(game_region, screenshot)
    print(f"There are {num_squares_x} squares horizontally and {num_squares_y} squares vertically.")
    return num_squares_x, num_squares_y
