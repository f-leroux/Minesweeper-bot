import random
import time
from game_io import init_game, click_square

def main():
    num_squares_x, num_squares_y = init_game()

    # Now let's randomly move the mouse to the center of 10 different squares
    for _ in range(10):
        grid_x, grid_y = random.randint(0, num_squares_x - 1), random.randint(0, num_squares_y - 1)
        click_square(grid_x, grid_y)
        time.sleep(0.5)
    
if __name__ == "__main__":
    main()