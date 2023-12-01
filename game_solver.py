def get_unrevealed_neighbors_coordinates(numbers, revealed_squares, x, y):
    unrevealed_neighbors_coordinates = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if (dx, dy) != (0, 0):
                if 0 <= x + dx < numbers.shape[0] and 0 <= y + dy < numbers.shape[1]:
                    if not revealed_squares[x + dx, y + dy]:
                        unrevealed_neighbors_coordinates.append((x + dx, y + dy))
    return unrevealed_neighbors_coordinates

def get_coords_to_click(numbers, revealed_squares, mines):
    # TODO: implement some second order logic, where the placement of mines for one square affects the placement of mines for another square
    mine_coords = set()
    # First pass to get all the squares that are guaranteed to be mines
    for x in range(numbers.shape[0]):
        for y in range(numbers.shape[1]):
            value = numbers[x, y]
            if value == 0: continue
            unrevealed_neighbors_coordinates = get_unrevealed_neighbors_coordinates(numbers, revealed_squares, x, y)
            not_revealed_count = len(unrevealed_neighbors_coordinates)
            mines_count = 0
            if not_revealed_count == value:
                mine_coords = mine_coords.union(unrevealed_neighbors_coordinates)
    for mine_coord in mine_coords:
        mines[mine_coord] = True

    coords_to_click = set()
    potential_guess_coords = set()
    # Second pass to get all the squares that are guaranteed to be safe
    for x in range(numbers.shape[0]):
        for y in range(numbers.shape[1]):
            value = numbers[x, y]
            if value == 0: continue
            unrevealed_neighbors_coordinates = get_unrevealed_neighbors_coordinates(numbers, revealed_squares, x, y)
            not_revealed_count = len(unrevealed_neighbors_coordinates)
            mines_count = 0
            for coord in unrevealed_neighbors_coordinates:
                if mines[coord]:
                    mines_count += 1
            if value == mines_count:
                for coord in unrevealed_neighbors_coordinates:
                    if not mines[coord]:
                        coords_to_click.add(coord)
            else:
                for coord in unrevealed_neighbors_coordinates:
                    if not mines[coord]:
                        potential_guess_coords.add(coord)
    coords_to_click = sorted(list(coords_to_click)) # So that the mouse doesn't move too much at once
    return mines, coords_to_click, potential_guess_coords