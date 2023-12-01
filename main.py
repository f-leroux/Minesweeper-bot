import random
from game_io import init_game, click_square, update_game_state
from game_solver import get_coords_to_click
import numpy as np


def main():
    revealed_squares, numbers, mines = init_game()
    num_squares_x, num_squares_y = revealed_squares.shape 

    # Randomly click one square at the start
    for _ in range(1):
        grid_x, grid_y = random.randint(0, num_squares_x - 1), random.randint(0, num_squares_y - 1)
        click_square(grid_x, grid_y)

    while True: 
        revealed_squares, numbers = update_game_state(revealed_squares, numbers)
        mines, coords_to_click, potential_guess_coords = get_coords_to_click(numbers, revealed_squares, mines)
        # print('Mines:\n', mines.T)
        # print('Revealed squares:\n', revealed_squares.T)
        # print('Numbers:\n', numbers.T)
        if np.all(revealed_squares | mines): break

        if not coords_to_click:
            print("No safe moves found. We have to guess.")
            print(potential_guess_coords)
            guess_coord = random.choice(list(potential_guess_coords))
            grid_x, grid_y = guess_coord
            click_square(grid_x, grid_y)

        for coord in coords_to_click:
            grid_x, grid_y = coord
            print(f"Clicking square at ({grid_x}, {grid_y})")
            click_square(grid_x, grid_y)
    
    
if __name__ == "__main__":
    main()