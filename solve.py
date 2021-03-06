################################################################################
#
# File: solve.py
# Author: Ken Sheedlo, modifications by Nick Vanderweit
# 
# A first^H^H^H^H^Hsecond hack at a Sudoku solver in Python.
#
################################################################################

import argparse

# State of board of fixed size
class Board(object):
    def __init__(self, infile=None):
        self.size = 9

        self.state = {}

        # Expect to read a line of dummy text (e.g., 'Grid 42')
        if not infile is None:
            if not infile.readline():
                raise EOFError()

        for i in xrange(self.size):
            # Fill in the board with zeros (unsolved)
            for j in xrange(self.size):
                self.state[(i,j)] = 0

            # If we have an input file, read in its row data
            if not infile is None:
                for (j, n) in enumerate(int(c) for c in infile.readline().strip()):
                    self.state[(i,j)] = n

    def get_num_entries(self):
        return len(self.state)

    # Searches the puzzle state for the unsolved position with the fewest
    # number of possibilities. Then yields a tuple of its row, column, and
    # a list of possible values based on what has been excluded by that row,
    # column, and box.
    def find_best_target(self):
        best_options = 10
        best_r, best_c = -1,-1
        best_valids = []
        for r in xrange(9):
            for c in xrange(9):
                if self.state[(r,c)] == 0:
                    # Count the number of options we have for this target.
                    # If less than best_options, save this position.
                    missing = [True for f in range(10)]

                    # Mark each solved number in this column as not valid for
                    # the solution at (r,c)
                    for check_r in xrange(9):
                        if self.state[(check_r, c)] != 0:
                            missing[self.state[(check_r, c)]] = False

                    # Mark each solved number in this row
                    for check_c in xrange(9):
                        if self.state[(r, check_c)] != 0:
                            missing[self.state[(r, check_c)]] = False
                    
                    # Determine the bounds of the 3x3 box and do the same for it
                    box_r = r / 3
                    box_c = c / 3
                    for br in xrange(3*box_r, 3*box_r + 3):
                        for bc in xrange(3*box_c, 3*box_c + 3):
                            if self.state[(br, bc)] != 0:
                                missing[self.state[(br, bc)]] = False
                    n_missing = len(filter(None, missing))
                    if n_missing < best_options:
                        # This is a better target than the previously-known
                        # one; replace
                        best_options = n_missing
                        best_r, best_c = r, c
                        best_valids = missing
        return best_r, best_c, best_valids
    
    # Solves the puzzle by finding the best target, sequentially substituting
    # all possible values, and recursing.
    def solve(self):
        row, column, valids = self.find_best_target()
        if len(valids) == 0:
            # Solved.
            return True

        for n in xrange(1, 10):
            if valids[n]:
                # Try each possible value for this square
                self.state[(row, column)] = n
                if self.solve():
                    return True

        self.state[(row, column)] = 0
        return False

    def validate(self):
        # Check rows
        for r in xrange(9):
            found = [False for n in xrange(10)]
            for c in xrange(9):
                found[self.state[(r, c)]] = True
            if len(filter(None, found[1:])) != 9:
                print str(self),
                raise Exception('validate: row {0} failed'.format(r))

        # Columns
        for c in xrange(9):
            found = [False for n in xrange(10)]
            for r in xrange(9):
                found[self.state[(r, c)]] = True
            if len(filter(None, found[1:])) != 9:
                print str(self),
                raise Exception('validate_board: column {0} failed'.format(c))
        
        # 3x3 Blocks
        for br in xrange(0, 9, 3):
            for bc in xrange(0, 9, 3):
                found = [False for n in xrange(10)]
                for r in xrange(br, br+3):
                    for c in range(bc, bc+3):
                        found[self.state[(r,c)]] = True
                if len(filter(None, found[1:])) != 9:
                    print str(self),
                    raise Exception('validate_board: block index {0},{1} failed'.format(br / 3, bc / 3))

    def __str__(self):
        lines = []
        for r in xrange(9):
            line = ''
            for c in xrange(9):
                if c % 3 == 0:
                    # Insert column padding between blocks
                    line += '   {0}'.format(self.state[(r, c)])
                else:
                    line += ' {0}'.format(self.state[(r, c)])
            if r % 3 == 0:
                # Insert column padding between rows
                lines.append('')
            lines.append(line)
        lines.append('')

        # Concatenate all the lines, separating them with a newline
        return ''.join(map(lambda l: l + "\n", lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Solve sudoku puzzles.')
    parser.add_argument('infile', metavar='file', type=file,
            help='filename to open')
    args = parser.parse_args()

    done = False
    nboards = 0
    total = 0
    while not done:
        try:
            board = Board(infile=args.infile)
            if board.get_num_entries() == 0:
                done = True
                break
            board.solve()
            board.validate()
            nboards = nboards + 1
            print "Solved board {0}".format(nboards)
        except EOFError:
            done = True
