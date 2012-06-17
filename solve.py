################################################################################
#
# File: solve.py
# Author: Ken Sheedlo
# 
# A first hack at a Sudoku solver in Python.
#
################################################################################

def index(r, c):
    return 9*r + c

def find_best_target(board):
    best_options = 10
    best_r, best_c = -1,-1
    best_valids = []
    for r in xrange(9):
        for c in xrange(9):
            if board[index(r,c)] == 0:
                # Count the number of options we have for this target.
                # If less than best_options, save this position.
                missing = [True for f in range(10)]
                for check_r in xrange(9):
                    if board[index(check_r, c)] != 0:
                        missing[board[index(check_r, c)]] = False
                for check_c in xrange(9):
                    if board[index(r, check_c)] != 0:
                        missing[board[index(r, check_c)]] = False
                box_r = r / 3
                box_c = c / 3
                for br in xrange(3*box_r, 3*box_r + 3):
                    for bc in xrange(3*box_c, 3*box_c + 3):
                        if board[index(br, bc)] != 0:
                            missing[board[index(br, bc)]] = False
                n_missing = len(filter(None, missing))
                if n_missing < best_options:
                    best_options = n_missing
                    best_r, best_c = r, c
                    best_valids = missing
    return best_r, best_c, best_valids

def solve(board):
    r, c, v = find_best_target(board)
    if len(v) == 0:
        # Solved.
        return True

    for n in xrange(1, 10):
        if v[n]:
            board[index(r, c)] = n
            if solve(board):
                return True
    board[index(r, c)] = 0
    return False

def print_board(board):
    for r in xrange(0, 81, 9):
        line = ''
        for c in xrange(9):
            if c % 3 == 0:
                line += '   {0}'.format(board[r + c])
            else:
                line += ' {0}'.format(board[r + c])
        if r % 27 == 0:
            print
        print line
    print

def load_board(f):
    # Expect to read a line of dummy text (e.g., 'Grid 42')
    f.readline()

    board = []
    for n in xrange(9):
        board.extend([int(c) for c in f.readline().strip()])
    return board

def validate_board(board):
    # Check rows
    for r in xrange(9):
        found = [False for n in xrange(10)]
        for c in xrange(9):
            found[board[index(r, c)]] = True
        if len(filter(None, found[1:])) != 9:
            print_board(board)
            raise Exception('validate_board: row {0} failed'.format(r))

    # Columns
    for c in xrange(9):
        found = [False for n in xrange(10)]
        for r in xrange(9):
            found[board[index(r, c)]] = True
        if len(filter(None, found[1:])) != 9:
            print_board(board)
            raise Exception('validate_board: column {0} failed'.format(c))
    
    # 3x3 Blocks
    for br in xrange(0, 9, 3):
        for bc in xrange(0, 9, 3):
            found = [False for n in xrange(10)]
            for r in xrange(br, br+3):
                for c in range(bc, bc+3):
                    found[board[index(r,c)]] = True
            if len(filter(None, found[1:])) != 9:
                print_board(board)
                raise Exception('validate_board: block index {0},{1} failed'.format(br / 3, bc / 3))
    


if __name__ == "__main__":
    f = open('sudoku.txt', 'r')
    done = False
    nboards = 0
    total = 0
    while not done:
        try:
            board = load_board(f)
            if len(board) == 0:
                done = True
                break
            solve(board)
            validate_board(board)
            total += 100 * board[0] + 10 * board[1] + board[2]
            nboards = nboards + 1
            print "Solved board {0}".format(nboards)
        except EOFError:
            done = True
    print total
