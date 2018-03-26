from __future__ import print_function
import random
import copy
from collections import deque
import pycosat
import time


class Grid:

    def __init__(self, problem):
        self.spots = [(i, j) for i in range(1, 10) for j in range(1, 10)]
        self.domains = {}
        # Need a dictionary that maps each spot to its related spots
        self.peers = {}
        self.box = {}
        self.row = {}
        self.col = {}
        for spot in self.spots:
            self.peers[spot] = set()
            self.row[spot] = set()
            self.col[spot] = set()
            self.box[spot] = set()
        self.parse(problem)
        self.peerEvaluation(self.spots)

    def parse(self, problem):
        for i in range(0, 9):
            for j in range(0, 9):
                c = problem[i * 9 + j]
                if c == '.':
                    self.domains[(i + 1, j + 1)] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                else:
                    self.domains[(i + 1, j + 1)] = [ord(c) - 48]

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                d = self.domains[(i + 1, j + 1)]
                if len(d) == 1:
                    print(d[0], end='')
                else:
                    print('.', end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")

    def peerEvaluation(self, spots):
        # returns the 9 boxes of sudoku as 9 sets of 9 spots each
        boxes = self.create_boxes(spots)
        for spot in spots:
            all_peers = set()
            for i in range(1, 10):  # box checking
                if spot in boxes[i]:
                    self.peers[spot] = self.peers[spot].union(boxes[i])
                    self.box[spot] = self.box[spot].union(boxes[i])
                    break
            # row checking and col checking
            for otherSpot in spots:
                if otherSpot == spot:
                    continue
                elif otherSpot[0] == spot[0]:
                    self.row[spot].add(otherSpot)
                    self.peers[spot].add(otherSpot)

                # the otherspot shares same spot as original spot
                elif otherSpot[1] == spot[1]:
                    self.col[spot].add(otherSpot)
                    self.peers[spot].add(otherSpot)
            self.box[spot].remove(spot)
            self.peers[spot].remove(spot)

    def create_boxes(self, spots):
        boxes = {}
        for i in range(1, 10):
            boxes[i] = set()

        for spot in spots:
            row = spot[0]
            col = spot[1]

            if 1 <= row <= 3 and 1 <= col <= 3:
                boxes[1].add(spot)
            elif 1 <= row <= 3 and 4 <= col <= 6:
                boxes[2].add(spot)
            elif 1 <= row <= 3 and 7 <= col <= 9:
                boxes[3].add(spot)
            #####################################
            elif 4 <= row <= 6 and 1 <= col <= 3:
                boxes[4].add(spot)
            elif 4 <= row <= 6 and 4 <= col <= 6:
                boxes[5].add(spot)
            elif 4 <= row <= 6 and 7 <= col <= 9:
                boxes[6].add(spot)
            ######################################
            elif 7 <= row <= 9 and 1 <= col <= 3:
                boxes[7].add(spot)
            elif 7 <= row <= 9 and 4 <= col <= 6:
                boxes[8].add(spot)
            elif 7 <= row <= 9 and 7 <= col <= 9:
                boxes[9].add(spot)
        return boxes


class EasySolver:

    def __init__(self, grid):
        # sigma is the assignment function
        self.sigma = {}
        self.grid = grid
        for k, v in self.grid.domains.items():
            self.sigma[k] = v[0] if len(v) == 1 else 0

    def display(self, sigma):

        for k, v in sigma.items():
            sigma[k] = [v]

        for i in range(0, 9):
            for j in range(0, 9):
                d = sigma[(i + 1, j + 1)]
                if len(d) == 1:
                    print(d[0], end='')
                else:
                    print('.', end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")

    def solve(self):  # this is like backtracking-search(csp) returns a solution or failure
        return self.search(self.sigma)

    def search(self, sigma):
        # self.display(copy.deepcopy(sigma))
        # print('-------------------------------------')
        # print()

        if 0 not in sigma.values():  # if assignment is complete, then return assignment
            for k, v in sigma.items():
                sigma[k] = [v]
            self.grid.domains = sigma
            return True
        spot = None
        for k, v, in sigma.items():
            if v == 0:
                spot = k  # assign the tuple
                break  # once found first, break
        # for each value in ORDER-DOMAIN-VALUES (var, assignment, csp) for the
        # spot
        for value in self.grid.domains[spot]:
            # if value is consistent with assignment then
            if self.consistent(spot, value, sigma):
                sigma[spot] = value  # add {var = value} to assignment1
                # sigma = self.infer(spot, sigma)
                original = copy.deepcopy(sigma)

                if self.simple_inference(spot, sigma):
                    if self.search(copy.deepcopy(sigma)):
                        return True

                sigma = original  # revert sigma back to original because not return true

        return False

    # I guess call this within infer
    # spot -> is the cell in question
    # value = val 1-9 coming from the Order-Domain-Values
    # grid -> has peers which can be used to check for consistency
    def consistent(self, spot, value, sigma):
        all_peers = self.grid.peers[spot]
        for peer in all_peers:  # peer is a tuple
            peer_value = sigma[peer]
            if peer_value is 0:  # if the value is 0 then no actual value has been established
                continue
            elif peer_value is value:  # peers should not have same values
                return False
        return True  # everything is consistent

    # for each call of infer, loop through each unfilled box in "assignment" and see
    # if we can reduce the domain of the box to a single number by checking
    # the row/col/box

    def simple_inference(self, spot, sigma):
        q = deque()
        q.append(spot)
        while len(q) > 0:
            spot = q.popleft()  # the spot for which u will be inferencing all the peers for
            all_peers = self.grid.peers[spot]
            for peer in all_peers:
                if sigma[peer] == 0:
                    value = self.reduce_value(peer, sigma)
                    if len(value) == 0:
                        return False  # with inference, shown that no spot is possible for this cell, so return False

                    elif len(value) == 1 and self.consistent(peer, value[0], sigma):
                        sigma[peer] = value[0]
                        q.append(peer)
        return True

    def reduce_value(self, spot, sigma):
        all_pears = self.grid.peers[spot]
        all = self.reduce_further(all_pears, sigma)
        return list(all)

    def reduce_further(self, peers, sigma):
        domain = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
        for peer in peers:
            val = sigma[peer]
            if val == 0:
                continue
            val = sigma[peer]
            if val in domain:
                domain.remove(val)
        return domain


class HardSolver:

    def __init__(self, grid):
        # sigma is the assignment function
        self.grid = grid
        self.sigma = copy.deepcopy(self.grid.domains)

    def consistent(self, spot, value, domain):
        all_peers = self.grid.peers[spot]
        for peer in all_peers:  # peer is a tuple
            peer_set = domain[peer]
            if len(peer_set) > 1:  # if the value is 0 then no actual value has been established
                continue
            # peers should not have same values
            elif len(peer_set) is 1 and peer_set[0] == value:
                return False
        return True  # everything is consistent

    def solve(self):  # this is like backtracking-search(csp) returns a solution or failure
        return self.search(self.sigma)

    def search(self, domain):
        stack = []
        stack.append(domain)
        while len(stack) > 0:
            domain = stack.pop()
            self.infer(domain)
            if self.not_empty(domain):
                spot = self.find_spot_with_multiple_candidates(domain)
                if spot is not None:
                    new_value = domain[spot].pop()
                    stack.append(copy.deepcopy(domain))
                    domain[spot] = [new_value]
                    for peer in self.grid.peers[spot]:
                        if new_value in domain[peer]:
                            domain[peer].remove(new_value)
                    stack.append(domain)
                else:
                    self.grid.domains = domain
                    return True
        return False

    def find_spot_with_multiple_candidates(self, domain):
        x = []
        y = []
        for spot in domain:
            length = len(domain[spot])
            if length > 1:
                x.append(spot)
                y.append(length)
        if len(x) == 0:
            return None
        else:
            index = y.index(min(y))
            return x[index]

    def not_empty(self, domain):
        for size in domain.values():
            if len(size) == 0:
                return False
        return True

    def infer(self, domain):
        q = deque()
        for spot in domain:
            if len(domain[spot]) > 1:
                q.append(spot)
        while len(q) > 1:
            spot = q.pop()
            self.simplify(spot, domain)
            if len(domain[spot]) == 1:
                for peer in self.grid.peers[spot]:
                    if len(domain[peer]) > 1:
                        q.append(peer)

    def simplify(self, spot, domain):
        # get all peers
        spot_candidates = domain[spot]
        peers_of_spot = self.grid.peers[spot]
        box_peers = self.grid.box[spot]
        row_peers = self.grid.row[spot]
        col_peers = self.grid.col[spot]
        for peer in peers_of_spot:
            peer_set = domain[peer]
            if len(peer_set) == 1:  # that means spot cannot have the value
                val = peer_set[0]
                if val in spot_candidates:

                    spot_candidates.remove(val)
                    if len(spot_candidates) == 1:
                        return
        # this checks uniqueness in box
        for value in spot_candidates:
            unique_value = True
            for peer in box_peers:
                peer_candidates = domain[peer]
                if value in peer_candidates:
                    unique_value = False
                    break
            if unique_value:
                domain[spot] = [value]
                return

        # this checks uniqueness in row
        for value in spot_candidates:
            unique_value = True
            for peer in row_peers:
                row_candidates = domain[peer]
                if value in row_candidates:
                    unique_value = False
                    break
            if unique_value:
                domain[spot] = [value]
                return

        # this checks uniqueness in col
        for value in spot_candidates:
            unique_value = True
            for peer in col_peers:
                col_candidates = domain[peer]
                if value in col_candidates:
                    unique_value = False
                    break
            if unique_value:
                domain[value] = [value]
                return


class SATSolver:

    def __init__(self, grid):
        self.grid = grid
        self.cnf = []

    def solve(self):
        self.encoding_numbers()
        self.restricting_rows_and_columns()
        self.restricting_boxes()
        self.initial_setup()
        result = pycosat.solve(self.cnf)
        if result is "UNSAT" or result is "UNKNOWN":
            return False
        else:
            for number in result:
                if number > 0:
                    num = str(number)
                    spot = (int(num[0]), int(num[1]))
                    self.grid.domains[spot] = num[2]
            return True

    def encoding_numbers(self):
        for i in range(1, 10):
            for j in range(1, 10):
                clause = []
                for n in range(1, 10):
                    number = str(i) + str(j) + str(n)
                    number = int(number)
                    clause.append(number)
                self.cnf.append(clause)
        for i in range(1, 10):
            for j in range(1, 10):
                for x in range(1, 9):
                    for y in range(x + 1, 10):
                        clause = []
                        ijx = str(i) + str(j) + str(x)
                        ijx = int(ijx)
                        ijx = -ijx
                        ijy = str(i) + str(j) + str(y)
                        ijy = int(ijy)
                        ijy = -ijy
                        clause.append(ijx)
                        clause.append(ijy)
                        self.cnf.append(clause)

    def restricting_rows_and_columns(self):
        # every row contains every number
        for i in range(1, 10):
            for n in range(1, 10):
                clause = []
                for j in range(1, 10):
                    ijn = str(i) + str(j) + str(n)
                    ijn = int(ijn)
                    clause.append(ijn)
                self.cnf.append(clause)

        # every column contains every number
        for j in range(1, 10):
            for n in range(1, 10):
                clause = []
                for i in range(1, 10):
                    ijn = str(i) + str(j) + str(n)
                    ijn = int(ijn)
                    clause.append(ijn)
                self.cnf.append(clause)

    def restricting_boxes(self):
        # every 3x3 box contains every number
        for r in range(0, 3):
            for s in range(0, 3):
                for n in range(1, 10):
                    clause = []
                    for i in range(1, 4):
                        for j in range(1, 4):
                            a = 3 * r + i
                            b = 3 * s + j
                            abn = str(a) + str(b) + str(n)
                            abn = int(abn)
                            clause.append(abn)
                    self.cnf.append(clause)

    def initial_setup(self):
        for spot in self.grid.domains:
            if len(self.grid.domains[spot]) == 1:
                i = spot[0]
                j = spot[1]
                n = self.grid.domains[spot][0]
                ijn = str(i) + str(j) + str(n)
                ijn = int(ijn)
                clause = [ijn]
                self.cnf.append(clause)

easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
        "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3"]

hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
        "52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

print("====Easy Problem====")
g = Grid(easy[0])
# Display the original problem
g.display()
s = EasySolver(g)
if s.solve():
    print("====Easy Solution===")
    # Display the solution
    # Feel free to call other functions to display
    g.display()
else:
    print("==No solution==")

print('---------------------------------------------')

print("====Easy Problem====")
g = Grid(easy[1])
# Display the original problem
g.display()
s = EasySolver(g)
if s.solve():
    print("====Easy Solution===")
    # Display the solution
    # Feel free to call other functions to display
    g.display()
else:
    print("==No solution==")

print('---------------------------------------------')
print("====Hard Problem====")
g = Grid(hard[0])
# Display the original problem
g.display()
s = HardSolver(g)
if s.solve():
    print("====Hard Solution===")
    # Display the solution
    # Feel free to call other functions to display
    g.display()
else:
    print("==No solution==")

print('---------------------------------------------')

print("====Hard Problem====")
g = Grid(hard[1])
# Display the original problem
g.display()
s = HardSolver(g)
if s.solve():
    print("====Hard Solution===")
    # Display the solution
    # Feel free to call other functions to display
    g.display()
else:
    print("==No solution==")

print("====SAT Hard Problem====")
g = Grid(hard[0])
g.display()
print('-------------------------')

s = SATSolver(g)
if s.solve():
    print("==== SAT Hard Solution===")
    g.display()
else:
    print("==No solution==")

print("====SAT Hard Problem====")
g = Grid(hard[1])
g.display()
print('-------------------------')
s = SATSolver(g)
if s.solve():
    print("==== SAT Hard Solution===")
    g.display()
else:
    print("==No solution==")

# print('----------------------------------------')
# print("Extra Credit 1")
# easy = []
# hard = []
#
# with open("easy.txt", "r") as ins:
#     for line in ins:
#         easy.append(line)
#
# with open("hard.txt", "r") as ins:
#     for line in ins:
#         hard.append(line)
#
# for line in hard:
#     print(line)
#
# easySolverTime = []
# hardSolverTime = []
# satSolverTime =  []
# for puzzle in hard:
#
#     # #easy solver
#     # g = Grid(puzzle)
#     # g.display()
#     # s = EasySolver(g)
#     # start = time.time()
#     # if s.solve():
#     #     g.display()
#     # else:
#     #     print("==No solution==")
#     # end = time.time()
#     # difference = end - start
#     # easySolverTime.append(difference)
#
#     #hard solver
#     g = Grid(puzzle)
#     # Display the original problem
#     g.display()
#     s = HardSolver(g)
#     start = time.time()
#     if s.solve():
#         # Display the solution
#         # Feel free to call other functions to display
#         g.display()
#     else:
#         print("==No solution==")
#     end = time.time()
#     difference = end - start
#     hardSolverTime.append(difference)
#
#     #sat solver
#     g = Grid(puzzle)
#     g.display()
#     s = SATSolver(g)
#     start = time.time()
#     if s.solve():
#         g.display()
#     else:
#         print("==No solution==")
#     end = time.time()
#     difference = end - start
#     satSolverTime.append(difference)
#
# # print("easy solver times")
# # for time in easySolverTime:
# #     print(time)
#
# print("hard solver times")
# for time in hardSolverTime:
#     print(time)
#
# print("sat solver times")
# for time in satSolverTime:
#     print(time)
