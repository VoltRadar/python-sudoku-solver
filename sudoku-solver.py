import numpy as np
import itertools
import copy


class SudokuState:
    """
    A class containing all methods and attributes needed to solve a sudoku puzzle
    """

    def __init__(self, state):
        """
        Input is a 9x9 numpy array of ints, with emtpy cells being
        zeros

        self.state is a 9x9 standard python list of ints if the value is known,
        or a list of numbers that it could possibly be
        """

        self.state = [[int(num) for num in row] for row in state]

        self.pairs = []

        # Changes the format of the state, turning every empty cell into a list of possible values that could be in
        # the space.
        self.setup()

    def setup(self):
        """
        Modifies the state such that all emtpy cells are replaced a list of
        numbers that could be in the cell
        """
        for position in itertools.product(range(9), repeat=2):
            # Runs though each item in the sudoku
            if self.state[position[0]][position[1]] == 0:
                # If the position is empty...

                possible_values = list(range(1, 10))  # Numbers that the value in position it could potentially be,
                # initialised as numbers 1 to 9

                # Runs though each neighbour to the position
                for neighbour_value in self.get_neighbors(position).values():
                    if type(neighbour_value) is int and neighbour_value > 0 and neighbour_value in possible_values:
                        # A neighbour has a given value, so the value for the position cannot include this neighbour
                        # value

                        possible_values.remove(neighbour_value)

                self.state[position[0]][position[1]] = possible_values[:]

    def get_neighbors(self, position, section=(True, True, True)):
        """
        Gets the 'neighbors' of given position. Doesn't return the input position
        The neighbors of a position is every number in it's row, it's column, and it's box by default.
        By setting

        Input:
            position: A iterable of 2 ints (row major order)

            section: A tuple of 3 booleans. all set to true by default
            Changing these values to only get neighbors from the position's row, column, or box.
            If section[0] = True, then it returns neighbors from the position's row.
            If section[1] = True, then it returns neighbors from the position's column.
            If section[2] = True, then it returns neighbors from the position's box.
            Multiple bools in section can be set to True

        Output: A dictionary with each key being a position (a pair of ints in a tuple), and it's value being a int
                if the space is solved, or a list of possible numbers.

                Note that the values are not copies of the values in the state. Modifying these values modifies the
                state directly
        """
        # The output dict. Will return this list at the end of the function
        output = {}

        # Adds the linked rows and columns

        if section[0] or section[1]:
            for i in range(9):
                if section[0]:
                    output[(position[0], i)] = self.state[position[0]][i]
                if section[1]:
                    output[(i, position[1])] = self.state[i][position[1]]

        if section[2]:
            # The position of the top left box that the position
            top_box_index = (position[0] - position[0] % 3, position[1] - position[1] % 3)

            # Looping though each number in the box and adds it to the output dictionary
            for box_pos in itertools.product(range(3), repeat=2):
                pos = (top_box_index[0] + box_pos[0], top_box_index[1] + box_pos[1])
                output[pos] = self.state[pos[0]][pos[1]]

        # Removes the input position from the output dictionary
        del output[position]

        return output

    def get_numpy_state(self):
        """
        Returns a numpy array of the state
        """
        return np.array([np.array([num for num in row]) for row in self.state])

    def get_empty_states(self):
        """
        Returns the states that are empty

        Input: None
        Output: Dict with keys of pairs of ints in a tuple, and values of the value of the
        square at that position.    Ruffly {position: self.state[position]}
        """
        output = {}
        for position in itertools.product(range(9), repeat=2):
            # For every position...

            value = self.state[position[0]][position[1]]
            if type(value) is list:
                output[position] = value

        return output

    def get_empty_neighbours(self, position, section=(True, True, True)):
        """
        Retuns the empty 'neighbours' of a given position

        Input:
            position: tuple containing 2 ints between 0 and 8, acting as an
            2d index for the square you want the empty neighbours of

            section: tuple of boolean if neighbours from the row, column, or box.
            By default, set to return every neighbour of the position
        Output:
            dict of empty neighbours in the form of {position of neighbour: list of possible values for neighbour}
        """
        neighbours = self.get_neighbors(position, section).copy()

        # If you don't convert neighbours.keys() to a list, then it will raise an
        # error when you change the length of the dictionary will the del
        # statement, which we really don't want

        for neighbours_position in list(neighbours.keys()):
            # if a given neighbour's value is known, then remove it from the neighbours dictionary
            if type(neighbours[neighbours_position]) is int:
                del neighbours[neighbours_position]

        return neighbours

    def get_numpy_proper_state(self, solvable):
        """
        Returns a numpy state with the empty states being replaced with 0s
        if it cannot be solved then every element will be replaced with -1
        """
        numpy_state = self.get_numpy_state()

        for position in itertools.product(range(9), repeat=2):
            if solvable == 0:
                if type(numpy_state[position[0]][position[1]]) is list:
                    numpy_state[position[0]][position[1]] = 0
            elif solvable == -1:
                numpy_state[position[0]][position[1]] = -1

        return numpy_state

    def remove_value(self, position, value):
        """Removes a value from a given position"""
        if type(self.state[position[0]][position[1]]) is list:
            self.state[position[0]][position[1]].remove(value)

    @staticmethod
    def is_neighbour(position1, position2):
        """
        Returns a True or False. Returns True if the two positions are neighbours of each other
        Returns False otherwise
        Returns False if the two positions are the same position
        """

        if position1 == position2:
            return False

        if position1[0] == position2[0]:
            return True

        if position1[1] == position2[1]:
            return True

        if (position1[0] // 3, position1[1] // 3) == (position2[0] // 3, position2[1] // 3):
            # In the same box
            return True

        return False

    def analise_empty_value(self, position):
        """
        Looks at a emtpy square and see's if it can remove some possible values
        from it's neighbours.
        If the emtpy value can only be one value, it fills in this value
        If it can remove possible values, it calls the remove values function.

        Returns -1 if the state is now unsolvable
        Returns 0 otherwise
        """

        # print("Current:")
        # print(self.get_numpy_proper_state(0))

        # print("Pos: ", position)

        current_possible_values = self.get_value_from_pos(position)

        # print("Values: ", current_possible_values)

        if type(current_possible_values) is int:
            # print("Int")
            # input("?")
            return 0

        if len(current_possible_values) == 0:
            # Sudoku was shown to be impossible
            return -1

        # A list containing dictionary's of all neighbours of the position including the position on
        # each row, col, and box
        # So emtpy_neighbour_sets[0] is every emtpy neighbour including itself on the positions row
        emtpy_neighbour_sets = []

        for i in range(3):
            section = (i == 0, i == 1, i == 2)
            emtpy_neighbour_set = self.get_empty_neighbours(position, section)
            emtpy_neighbour_set[position] = current_possible_values.copy()

            emtpy_neighbour_sets.append(emtpy_neighbour_set)

        for index, emtpy_neighbour_set in enumerate(emtpy_neighbour_sets):
            # Dictionary of values 1 to 9, with values of a list of positions this value could be in
            # If a number has a count of one, then it must be in the position where it's possible, and we can fill it in

            # Worth pointing out that if a value has a count of 0, that's okay, as it will be filled in in this row,
            # col, or box
            counts = {v: [] for v in range(1, 10)}

            for value in counts:
                for pos, possible_values in emtpy_neighbour_set.items():
                    if value in possible_values:
                        counts[value].append(pos)

                # Check to see if the value could only be in one square, and if that's true, fill in this value at
                # that square
                # Also checks to see if that square has already been filled in, in which case we ignore it
                if len(counts[value]) == 1 and type(self.get_value_from_pos(counts[value][0])) is list:
                    # print("Found")
                    # print("Value: ", value)
                    # print("Pos: ", counts[value][0])
                    # print(emtpy_neighbour_set)

                    outcome = self.fill_in_square(counts[value][0], value)
                    # print("Outcome: ", outcome)

                    if outcome == -1:
                        # Sudoku was shown to be unsolvable
                        return -1

        return 0

    def get_sets(self, position):
        """
        Returns a list of dictionary that is the row of this position, the column of the position,
        and the box of this position

        Both empty and non empty squares are included
        The input position is included
        """
        output = []
        for i in range(3):
            section = [False, False, False]
            section[i] = True
            set = self.get_neighbors(position, section)
            set[position] = self.get_value_from_pos(position)
            output.append(set.copy())

        return output.copy()

    def get_value_from_pos(self, position):
        """Returns the value of the state at a given position"""
        return self.state[position[0]][position[1]]

    def fill_in_square(self, position, value):
        """
        Updates the value of an empty square to a value given.
        Then recursively updates values of neighbouring squares that have had possibilities
        removed that can now be filled in

        Inputs:
            position: tuple containing 2 ints between 0 and 8, which is the index of the square you want to fill in
            value: int, which is the value that you want to update the given square to
        Output:
            int, if output = 0, then it filled in fine and found no contractions (empty squares with no possible values
            that they could be)
            if output = -1, then a empty square with no possible values that the square could be was found. This would
            mean that the state when the root function was first called is impossible to solve.
            also returns -1 if the given position is not empty
        """

        empty_neighbours = self.get_empty_neighbours(position)

        if type(self.state[position[0]][position[1]]) is list:
            # Updates the value of the square at the given position
            self.state[position[0]][position[1]] = value
        else:
            return -2

        # List of positions that are reduced
        reduced_positions = []

        # Remove the value from empty neighbours that have the possibility of being the given value
        # These empty neighbours are more likely to be able to filled in, and should be checked
        # if they can now be filled in
        for neighbour_position in list(empty_neighbours.keys()):
            if value in empty_neighbours[neighbour_position]:
                # Remove it from the empty neighbour
                self.remove_value(neighbour_position, value)
                reduced_positions.append(neighbour_position)

            elif not empty_neighbours[neighbour_position]:
                # This state is impossible to solve with this move
                return -1

        # Checking all the reduced positions
        for reduced_position in reduced_positions:
            # Checking if the removed possible value finds that the sudoku is impossible
            # Will also fill in other values if it can
            if self.analise_empty_value(reduced_position) == -1:
                return -1

            if type(self.get_value_from_pos(reduced_position)) is int:
                # We were able to fill in this value by considering empty values:
                continue

            if len(self.get_value_from_pos(reduced_position)) == 0:
                # Sudoku is now unsolvable
                return -1

            elif len(self.get_value_from_pos(reduced_position)) == 1:
                # Recursive call, as now this reduced position can be filled in

                recursive_result = self.fill_in_square(reduced_position, empty_neighbours[reduced_position][0])
                if recursive_result == -2:
                    pass

                # If the result of the sudoku is unsolvable after filling in the reduced neighbour
                # then this sudoku will be unsolvable
                if recursive_result == -1:
                    return -1

        return 0

    def narrow(self):
        """
        Narrows down the sudoku, filling in all positions that can be filled in, and removing some possible
        values.
        Will not do this completely, but will never guess.

        It will also check every row, column, and box to make sure that every value can be or is in this row, column,
        or box

        Returns an int.
            returns 0 if not finished but found no contradictions
            returns 1 if the sudoku is now solved
            returns -1 if the sudoku was found to be unsolvable
        """

        # These positions are all in unique rows, columns, and boxes
        for position in [(0, 0), (1, 3), (2, 6), (3, 1), (4, 4), (5, 7), (6, 2), (7, 5), (8, 8)]:
            for neighbour_set in self.get_sets(position):
                # A neighbour_set is a collective name for a row, column, or box that has that position
                for value in range(1, 10):

                    # Is the value already filled in?
                    if value in neighbour_set.values():
                        continue

                    value_possible = False
                    for neighbour_set_value in neighbour_set.values():
                        if type(neighbour_set_value) is list and value in neighbour_set_value:
                            value_possible = True
                            break

                    # Is value possible to be in this row, column, or box
                    if not value_possible:
                        return -1



        # dict of all the empty positions in the state
        emtpy_squares = self.get_empty_states()

        # If the number of empty squares is zero, then the sudoku is solved
        if len(emtpy_squares) == 0:
            return 1

        # Goes though every empty square in the sudoku to see if it can be filled in
        for empty_pos in list(emtpy_squares.keys()):
            if type(self.get_value_from_pos(empty_pos)) is int:
                # We have changed this emtpy position and filled it in.
                # Just continue to the next empty position
                continue

            # If we can fill in this square, fill it in
            if len(self.get_value_from_pos(empty_pos)) == 1:
                outcome = self.fill_in_square(empty_pos, emtpy_squares[empty_pos][0])

                if outcome == -1:
                    return -1

                if outcome == -2:
                    pass

            elif len(self.get_value_from_pos(empty_pos)) == 0:
                # This sudoku can not solved
                return -1

        # If we were not able to fill in a square, then the function can not fill in
        # a square, so the function must end
        return 0

    def check(self):
        """
        Checks the current state to see if there are contradictions already in the sudoku
        Returns -1 if 2 or more neighbouring squares have the same value
        Also returns -1 if an emtpy square which has no possible values it could be
        Returns 0 otherwise
        """
        for position in itertools.product(range(9), repeat=2):
            value = self.state[position[0]][position[1]]
            if type(value) is int and value in self.get_neighbors(position).values():
                return -1
        return 0

    def is_solved(self):
        """Returns 1 if solved, returns 0 otherwise"""
        for position in itertools.product(range(9), repeat=2):
            if type(self.get_value_from_pos(position)) is list:
                return 0
        return 1

    def least_constraining_value(self, position):
        """
        Takes as input the position of an empty space, and returns the value
        that the empty state would need to take, to constrain the neighbouring
        states the least

        Input: tuple of a postion in the state
        Output: int of a value it could take
        """

        values = self.state[position[0]][position[1]]

        empty_neighbours = self.get_empty_neighbours(position)

        # The number of neighbours that has a possible value of a given value
        constraints = {v: 0 for v in values}

        # Running though all the possible neighbours.
        for possible_empty_neighbours_values in empty_neighbours.values():
            for value in values:
                if value in possible_empty_neighbours_values:
                    constraints[value] += 1

        constraints = list(constraints.items())
        constraints.sort(key=lambda x: x[1])

        return constraints[0][0]

    def solve(self):
        """
        Changes the state into a solved sudoku if it can.
        This function is recursive

        Returns 1 if the sudoku was solved
        Returns -1 if the sudoku was unsolvable
        """
        # Narrows down possible options until there are at least 2 possible options for every empty square,
        # or it was solved or shown to be unsolvable
        outcome = self.narrow()

        # If the outcome is not zero, then the sudoku is solved or known to be unsolvable
        if outcome != 0:
            return outcome

        if self.is_solved() == 1:
            return 1

        # Will now find the solution by guessing

        # The position of the square with the least number of possible values it could be
        # Implementation of Minimum remaining values heuristic
        square_to_edit = sorted(list(self.get_empty_states().items()), key=lambda x: len(x[1]))[0][0]

        # A copy of the state
        state_copy = copy.deepcopy(self.state)

        # While there are values at the square to edit
        while type(self.get_value_from_pos(square_to_edit)) is list and self.get_value_from_pos(square_to_edit):
            guess_of_value = self.least_constraining_value(square_to_edit)

            # Fill in the value
            outcome_of_guess = self.fill_in_square(square_to_edit, guess_of_value)

            if outcome_of_guess == 0:
                outcome_of_guess = self.solve()

            # outcome_of_guess is 1 if the sudoku is from the guess solved,
            # and -1 if the sudoku is unsolvable from the guess

            # if the outcome is 1, then the sudoku is solved
            if outcome_of_guess == 1:
                return 1

            if outcome_of_guess == -1:
                # If the sudoku was unsolvable, then square_to_edit cannot
                # be in possible values.
                # Remove it from possible values, and analise it to see if that
                # gives us a little more information
                self.state = copy.deepcopy(state_copy)
                self.remove_value(square_to_edit, guess_of_value)

                # If this is -1, then the removed value made this sudoku unsolvable
                outcome_of_analysis = self.analise_empty_value(square_to_edit)

                if outcome_of_analysis == -1:
                    return -1

                # Updates the state copy, as values have changed
                state_copy = copy.deepcopy(self.state)

        value_at_edited_square = self.get_value_from_pos(square_to_edit)
        if type(value_at_edited_square) is list:
            return -1

        else:
            return self.solve()

    def get_solved_numpy(self):
        """
        Solves the sudoku. Returns a 9X9 numpy 2d list of the solved sudoku.
        If the sudoku is unsolvable, then all values will be -1
        """
        # checks to see if this sudoku can be shown quickly to be unsolvable
        # self.check will be -1 if this is the case
        is_already_unsolvable = self.check()

        # If it's already unsolvable, then we can simply modify the state,
        # and return it as a numpy state
        if is_already_unsolvable == -1:
            return self.get_numpy_proper_state(-1)

        # If it's not shown to be unsolvable, then try to solve it with a recurive solver
        else:
            return self.get_numpy_proper_state(self.solve())


def sudoku_solver(sudoku_puzzle):
    """
    Solves a Sudoku puzzle and returns its unique solution.

    Input
        sudoku : 9x9 numpy array
            Empty cells are designated by 0.

    Output
        9x9 numpy array of integers
            It contains the solution, if there is one. If there is no solution, all array entries should be -1.
    """

    sudoku_puzzle = SudokuState(sudoku_puzzle)
    return sudoku_puzzle.get_solved_numpy()