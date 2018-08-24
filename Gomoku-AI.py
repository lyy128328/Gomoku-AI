from math import *
import random
import numpy as np
import time
from sys import exit

class Gomoku:
    # A state of the game, i.e. the game board is a N*N matrix
    # where 0 = 0, 1 = player, 2 = computer
    def __init__(self):
        self.playerJustMoved = 2 # At the root pretend the player just moved is p2 - p1 has the first move
        self.N = 15
        self.winner = 0
        self.moved = []
        self.board = np.zeros([self.N, self.N])
        self.playerStepCount = 0
        self.steps = []
        
    def Regret(self):
        self.playerStepCount -= 1
        m = self.steps[-1]
        self.board[m[0]][m[1]] = 0
        del self.steps[-1]
        m = self.steps[-1]
        self.board[m[0]][m[1]] = 0
        del self.steps[-1]
        self.moved = self.steps[-1]
        self.winner = 0
        
    def SetFirst(self, player):
        self.playerJustMoved = 3 - player

    def Clone(self):
        # Create a deep clone of this game state.
        st = Gomoku()
        st.playerJustMoved = self.playerJustMoved
        st.N = self.N
        st.board = self.board.copy()
        st.winner = self.winner
        st.moved = self.moved[:]
        return st

    def DoMove(self, move):
        # Update a state by carrying out the given move.
        # Must update playerToMove.
        #assert move >= 0 and move <= self.N*self.N and move == int(move) and self.board[move] == 0
        self.playerJustMoved = 3 - self.playerJustMoved
        self.board[move[0], move[1]] = self.playerJustMoved
        self.moved = move
        self.CheckWinner()

    def GetMoves(self):
        # Get all possible moves from this state.
        return np.argwhere(self.board == 0).tolist()

    def CheckBoard(self, move, player):
        # Check marks given for this move and this player
        dirs = [[1,-1], [1,0], [1,1], [0,1]]
        mark = 0
        for d in dirs:
            upCount = 1
            [y,x] = move
            upAlive = False
            for i in range(1,5):
                y += d[0]*-1
                x += d[1]*-1
                if x < self.N and x >= 0 and y < self.N and y >= 0:
                    if self.board[y,x] == player:
                        upCount += 1
                    elif self.board[y,x] == 0:
                        upAlive = True
                        break
                    else:
                        upAlive = False
                        break
                else:
                    upAlive = False
                    break

            downCount = 1
            [y,x] = move
            for i in range(1,5):
                y += d[0]
                x += d[1]
                if x < self.N and x >= 0 and y < self.N and y >= 0:
                    if self.board[y,x] == player:
                        downCount += 1
                    elif self.board[y,x] == 0:
                        downAlive = True
                        break
                    else:
                        downAlive = False
                        break
                else:
                    downAlive = False
                    break      

            count = upCount + downCount - 1
            # if 5 connected or 4 connected and alive
            if count >= 5 or count >= 4 and downAlive and upAlive:
                mark += 1
            # if 3 connected and alive, or 4 connected and half alive
            elif count >= 3 and downAlive and upAlive or count >= 4 and (upAlive or downAlive):
                mark += 0.5
        return mark 

    def CheckWinner(self):
        mark = self.CheckBoard(self.moved, self.playerJustMoved)
        if mark >= 1:
            self.winner = self.playerJustMoved

    def GetScore(self, move):
        player = 3 - self.playerJustMoved
        mark = self.CheckBoard(move, player)

        state = self.Clone()
        state.board[move[0], move[1]] = player
        state.CheckWinner();

        if state.winner == state.playerJustMoved:
            mark -= 0.8
        return mark  

    def GetResult(self, playerjm):
        # Get the game result from the viewpoint of playerjm. 
        if self.winner == playerjm:
            return 1
        elif self.winner == 0:
            return 0.5
        else:
            return 0

    def __repr__(self):
        s = "  0 1 2 3 4 5 6 7 8 91011121314\n"
        for i in range(self.N):
            s += str(chr(ord('A') + i)) + " "
            for j in range(self.N):
                s += "-XO"[int(self.board[i,j])] + " "
            s += "\n"
        return s
    
    def get_column(self, y, x, length=5):
        line = np.empty(length, dtype='int8')
        for i in range(length):
            line[i] = self.board[y+i,x]
        return line, [(y+i,x) for i in range(length)]

    def get_row(self, y, x, length=5):
        line = np.empty(length, dtype='int8')
        for i in range(length):
            line[i] = self.board[y,x+i]
        return line, [(y,x+i) for i in range(length)]

    def get_diagonal_upleft_to_lowright(self, y, x, length=5):
        line = np.empty(length, dtype='int8')
        for i in range(length):
            line[i] = self.board[y+i,x+i]
        return line, [(y+i,x+i) for i in range(length)]

    def get_diagonal_lowleft_to_upright(self, y, x, length=5):
        line = np.empty(length, dtype='int8')
        if y < length - 1:
            raise IndexError
        for i in range(length):
            line[i] = self.board[y-i,x+i]
        return line, [(y-i,x+i) for i in range(length)]
    
    def line_getter_functions(self, state, length=5):
        return [lambda x,y: state.get_column(x,y,length=length), lambda x,y: state.get_row(x,y, length=length),
                lambda x,y: state.get_diagonal_upleft_to_lowright(x,y, length=length),
                lambda x,y: state.get_diagonal_lowleft_to_upright(x,y, length=length)]

    def extend_one(self, state):
        "Place a stone next to another one but only if extendable to five."
        for i in range(15):
            for j in range(15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # search pattern: one of own color and four 0
                    if len(np.where(line == 0)[0]) == 4 and len(np.where(line == 3-state.playerJustMoved)[0]) == 1:
                        index_own_color = np.where(line == 3-state.playerJustMoved)[0][0]
                        if index_own_color == 0:
                            m = positions[1]
                            print "extend_one"
                            print "Move: " + str(m) + "\n"
                            state.DoMove(m)
                            state.steps.append(m)
                            return True
                        else:
                            m = positions[index_own_color - 1]
                            print "extend_one"
                            print "Move: " + str(m) + "\n"
                            state.DoMove(m)
                            state.steps.append(m)
                            return True
        return False

    def block_open_four(self, state):
        "Block a line of four stones if at least one end open."
        for i in range (15):
            for j in range (15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i, j)
                    except IndexError:
                        continue

                    # selection: search four of opponent's color and one 0
                    if len(np.where(line == 0)[0]) == 1 and len(np.where(line == state.playerJustMoved)[0]) == 4:
                        index_of_0 = np.where(line == 0)[0][0]
                        m = positions[index_of_0]
                        print "block_open_four"
                        print "Move: " + str(m) + "\n"
                        state.DoMove(m)
                        state.steps.append(m)
                        return True
        return False

    def block_doubly_open_two(self, state):
        "Block a line of two if both sides are open."
        for i in range (15):
            for j in range (15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue

                    # select pattern [<all 0>, <opponent's color>, <opponent's color>, <all 0>]
                    if ( line == (0, state.playerJustMoved, state.playerJustMoved, 0, 0) ).all():
                        m = positions[3]
                        print "block_doubly_open_two"
                        print "Move: " + str(m) + "\n"
                        state.DoMove(m)
                        state.steps.append(m)
                        return True

                    elif ( line == (0, 0, state.playerJustMoved, state.playerJustMoved, 0) ).all():
                        m = positions[1]
                        print "block_doubly_open_two"
                        print "Move: " + str(m) + "\n"
                        state.DoMove(m)
                        state.steps.append(m)
                        return True
        return False

    def block_twice_to_three_or_more(self, state):
        "Prevent opponent from closing two lines of three or more simultaneously."
        line_getter_functions = self.line_getter_functions(state)
        line_positions = []
        getter_functions = []
        for i in range (15):
            for j in range (15):
                for f in line_getter_functions:
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # search two of opponent's color and three 0 in two crossing lines at an 0 position
                    opponent_stones_in_line = len(np.where(line == state.playerJustMoved)[0])
                    if opponent_stones_in_line >= 2 and len(np.where(line == 0)[0]) == 5 - opponent_stones_in_line:
                        for oldpos, old_getter in zip(line_positions, getter_functions):
                            for pos in positions:
                                if f != old_getter and pos in oldpos and state.board[pos] == 0:
                                    m = pos
                                    print "block_twice_to_three_or_more"
                                    print "Move: " + str(m) + "\n"
                                    state.DoMove(m)
                                    state.steps.append(m)
                                    return True
                        line_positions.append(positions)
                        getter_functions.append(f)
        return False
    
    def block_twice_to_four(self, state):
        "Prevent opponent from closing two lines of four simultaneously."
        line_getter_functions = self.line_getter_functions(state)
        line_positions = []
        getter_functions = []
        for i in range (15):
            for j in range (15):
                for f in line_getter_functions:
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # search two of opponent's color and three 0 in two crossing lines at an 0 position
                    opponent_stones_in_line = len(np.where(line == state.playerJustMoved)[0])
                    if opponent_stones_in_line == 3 and len(np.where(line == 0)[0]) == 2:
                        for oldpos, old_getter in zip(line_positions, getter_functions):
                            for pos in positions:
                                if f != old_getter and pos in oldpos and state.board[pos] == 0:
                                    m = pos
                                    print "block_twice_to_four"
                                    print "Move: " + str(m) + "\n"
                                    state.DoMove(m)
                                    state.steps.append(m)
                                    return True
                        line_positions.append(positions)
                        getter_functions.append(f)        
        return False
    
    def block_twice_to_three(self, state):
        "Prevent opponent from closing two lines of three simultaneously."
        line_getter_functions = self.line_getter_functions(state)
        line_positions = []
        getter_functions = []
        for i in range (15):
            for j in range (15):
                for f in line_getter_functions:
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # search two of opponent's color and three 0 in two crossing lines at an 0 position
                    opponent_stones_in_line = len(np.where(line == state.playerJustMoved)[0])
                    if opponent_stones_in_line == 2 and len(np.where(line == 0)[0]) == 3:
                        for oldpos, old_getter in zip(line_positions, getter_functions):
                            for pos in positions:
                                if f != old_getter and pos in oldpos and state.board[pos] == 0:
                                    m = pos
                                    print "block_twice_to_three"
                                    print "Move: " + str(m) + "\n"
                                    state.DoMove(m)
                                    state.steps.append(m)
                                    return True
                        line_positions.append(positions)
                        getter_functions.append(f)        
        return False

    def block_open_three(self, state):
        "Block a line of three."
        for i in range (15):
            for j in range (15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue

                    # selection: search three of opponent's color and two 0
                    if len(np.where(line == 0)[0]) == 2 and len(np.where(line == state.playerJustMoved)[0]) == 3:
                        indices_opponent = np.where(line == state.playerJustMoved)[0]
                        if not (indices_opponent[1] == indices_opponent[0] + 1 and
                                indices_opponent[2] == indices_opponent[1] + 1):
                                    continue
                        if 0 not in indices_opponent:
                            m = positions[indices_opponent[0] - 1]
                            print "block_open_three"
                            print "Move: " + str(m) + "\n"
                            state.DoMove(m)
                            state.steps.append(m)
                            return True
                        else:
                            m = positions[3]
                            print "block_open_three"
                            print "Move: " + str(m) + "\n"
                            state.DoMove(m)
                            state.steps.append(m)
                            return True
        return False

    def block_open_two(self, state):
        "Block a line of two."
        for i in range (15):
            for j in range (15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # selection: search pattern [<all 0 or bpundary>, opponent, opponent, <all 0 or boundary>]
                    if len(np.where(line == 0)[0]) == 3 and len(np.where(line == state.playerJustMoved)[0]) == 2:
                        indices_opponent = np.where(line == state.playerJustMoved)[0]
                        if indices_opponent[1] == indices_opponent[0] + 1:
                            if indices_opponent[0] == 0:
                                m = positions[3]
                                print "block_open_two"
                                print "Move: " + str(m) + "\n"
                                state.DoMove(m)
                                state.steps.append(m)
                                return True
                            else:
                                m = positions[indices_opponent[0]-1]
                                print "block_open_two"
                                print "Move: " + str(m) + "\n"
                                state.DoMove(m)
                                state.steps.append(m)
                                return True
        return False

    def block_doubly_open_three(self, state):
        "Block a line of three but only if both sides are open."
        for i in range(15):
            for j in range(15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue

                    if ( line == (0, state.playerJustMoved, state.playerJustMoved, state.playerJustMoved, 0) ).all():
                        bestR = 0
                        bestC = 0
                        bestScore = -9999
                        attack = 1
                        guard = 2
                        AI = 2
                        player = 1
                        
                        m = positions[0]
                        attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                        guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                        score = attackScore+guardScore
                        if (score > bestScore):
                            bestR = m[0]
                            bestC = m[1]
                            bestScore = score
                            
                        m = positions[4]
                        attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                        guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                        score = attackScore+guardScore
                        if (score > bestScore):
                            bestR = m[0]
                            bestC = m[1]
                            bestScore = score

                        m = [bestR, bestC]
                        print "block_doubly_open_three"
                        print "Move: " + str(m) + "\n"
                        state.DoMove(m)
                        state.steps.append(m)
                        return True
        return False

    def extend_three_to_four(self, state):
        "Extend a line of three stones to a line of four stones but only if there is enough space to be completed to five."
        for i in range(15):
            for j in range(15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # selection: search three of own color and two 0
                    if len(np.where(line == 0)[0]) == 2 and len(np.where(line == 3-state.playerJustMoved)[0]) == 3:
                        indices_0 = np.where(line == 0)[0]
                    
                        bestR = 0
                        bestC = 0
                        bestScore = -9999
                        attack = 1
                        guard = 2
                        AI = 2
                        player = 1
                        
                        m = positions[indices_0[0]]
                        attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                        guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                        score = attackScore+guardScore
                        if (score > bestScore):
                            bestR = m[0]
                            bestC = m[1]
                            bestScore = score
                            
                        m = positions[indices_0[1]]
                        attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                        guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                        score = attackScore+guardScore
                        if (score > bestScore):
                            bestR = m[0]
                            bestC = m[1]
                            bestScore = score

                        m = [bestR, bestC]
                        print "extend_three_to_four"
                        print "Move: " + str(m) + "\n"
                        state.DoMove(m)
                        state.steps.append(m)
                        return True
        return False

    def block_to_doubly_open_four(self, state):
        "Prevent the opponent from getting a line of four with both ends open."
        for i in range(15):
            for j in range(15):
                for f in self.line_getter_functions(state, length=6):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # selection: search pattern [0, <extendable to 4 times opponent>, 0]
                    if len(np.where(line == 0)[0]) == 3 and len(np.where(line == state.playerJustMoved)[0]) == 3:
                        indices_0 = np.where(line == 0)[0]
                        if not (line[0] == 0 and line[-1] == 0):
                            continue
                        else:
                            bestR = 0
                            bestC = 0
                            bestScore = -9999
                            attack = 1
                            guard = 2
                            AI = 2
                            player = 1
                            
                            if line[1] == 0:
                                m = positions[1]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = positions[5]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = [bestR, bestC]
                                print "block_to_doubly_open_four"
                                print "Move: " + str(m) + "\n"
                                state.DoMove(m)
                                state.steps.append(m)
                                return True
                            elif line[2] == 0:
                                m = positions[0]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score
                                    
                                m = positions[2]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = positions[5]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = [bestR, bestC]
                                print "block_to_doubly_open_four"
                                print "Move: " + str(m) + "\n"
                                state.DoMove(m)
                                state.steps.append(m)
                                return True
                            elif line[3] == 0:
                                m = positions[0]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score
                                    
                                m = positions[3]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = positions[5]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = [bestR, bestC]
                                print "block_to_doubly_open_four"
                                print "Move: " + str(m) + "\n"
                                state.DoMove(m)
                                state.steps.append(m)
                                return True
                            elif line[4] == 0:
                                m = positions[0]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = positions[4]
                                attackScore = state.getScore(state, m[0], m[1], AI, attack) # 攻擊分數
                                guardScore  = state.getScore(state, m[0], m[1], player, guard) # 防守分數
                                score = attackScore+guardScore
                                if (score > bestScore):
                                    bestR = m[0]
                                    bestC = m[1]
                                    bestScore = score

                                m = [bestR, bestC]
                                print "block_to_doubly_open_four"
                                print "Move: " + str(m) + "\n"
                                state.DoMove(m)
                                state.steps.append(m)
                                return True
        return False

    def extend_three_to_doubly_open_four(self, state):
        """ 
        Extend a line of three stones to a line of four stones but only
        if there is enough space to be completed to five ON BOTH SIDES.
        """
        for i in range(15):
            for j in range(15):
                for f in self.line_getter_functions(state, length=6):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # selection: search pattern [0, <extendable to 4 times own>, 0]
                    if len(np.where(line == 0)[0]) == 3 and len(np.where(line == 3-state.playerJustMoved)[0]) == 3:
                        indices_0 = np.where(line == 0)[0]
                        if not (line[0] == 0 and line[-1] == 0):
                            continue
                        else:
                            m = positions[indices_0[1]]
                            print "extend_three_to_doubly_open_four"
                            print "Move: " + str(m) + "\n"
                            state.DoMove(m)
                            state.steps.append(m)
                            return True
        return False

    def extend_two_to_three(self, state):
        """ 
        Extend a line of two stones to a line of three stones but only
        if there is enough space to be completed to five.
        """
        for i in range(15):
            for j in range(15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # selection: search two of own color and three 0
                    if len(np.where(line == 0)[0]) == 3 and len(np.where(line == 3-state.playerJustMoved)[0]) == 2:
                        indices_0 = np.where(line == 0)[0]
                        m = positions[indices_0[np.random.randint(3)]]
                        print "extend_two_to_three"
                        print "Move: " + str(m) + "\n"
                        state.DoMove(m)
                        state.steps.append(m)
                        return True
        return False

    def extend_twice_two_to_three(self, state):
        """
        Extend two crossing lines of two stones to two lines of three
        stones but only if there is enough space to be completed to five.
        """
        line_positions = []
        getter_functions = []
        for f in self.line_getter_functions(state):
            for i in range(15):
                for j in range(15):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # search two of own color and three 0 in two crossing lines at an 0 position
                    if len(np.where(line == 0)[0]) == 3 and len(np.where(line == 3-state.playerJustMoved)[0]) == 2:
                        for oldpos, old_getter in zip(line_positions, getter_functions):
                            for pos in positions:
                                if f != old_getter and pos in oldpos and state.board[pos] == 0:
                                    m = pos
                                    print "extend_twice_two_to_three"
                                    print "Move: " + str(m) + "\n"
                                    state.DoMove(m)
                                    state.steps.append(m)
                                    return True
                        line_positions.append(positions)
                        getter_functions.append(f)
        return False
    
    def sequential_move(self, state):
        for i in range (1, 14):
            for j in range (1, 14):
                if state.board[i, j] == 0:
                    around = 0
                    for x in range (i-1, i+2):
                        for y in range (j-1, j+2):
                            around += state.board[x, y]
                            if around != 0:
                                m = [i, j]
                                print "sequential_move"
                                print "Move: " + str(m) + "\n"
                                state.DoMove(m)
                                state.steps.append(m)
                                return True
        return False     
    
    def random_move(self, state):
        for i in range (15):
            for j in range (15):
                if state.board[i, j] == 0:
                    m = [i, j]
                    print "random_move"
                    print "Move: " + str(m) + "\n"
                    state.DoMove(m)
                    state.steps.append(m)
                    return True
        return False        

    def check_if_immediate_win_possible(self, state):
        """
        Check if it is possible to place a stone such thath the player wins
        immediately.
        Return the position to place the stone if possible, otherwise return None.
        """
        for i in range(15):
            for j in range(15):
                for f in self.line_getter_functions(state):
                    try:
                        line, positions = f(i,j)
                    except IndexError:
                        continue
                    # selection:
                    #            - can only place stones where field is ``0``
                    #            - line must sum to "+" or "-" 4 (4 times black=+1 or white=-1 and once 0=0)

                    # place stone if that leads to winning the game
                    if 0 in line and line.sum() == (3-state.playerJustMoved) * 4:
                        for pos in positions:
                            if state.board[pos] == 0:
                                return pos
                        raise RuntimeError("Check the implementation of ``check_if_immediate_win_possible``.")
        # control reaches this point only if no winning move is found => return None

    def win_if_possible(self, state):
        """
        Place a stone where the player wins immediately if possible.
        Return ``True`` if a stone has been placed, otherwise return False.
        """
        pos = self.check_if_immediate_win_possible(state)
        if pos is None:
            return False
        else:
            m = pos
            print "win_if_possible"
            print "Move: " + str(m) + "\n"
            state.DoMove(m)
            state.steps.append(m)
            return True
    
    def patternCheck(self, state, turn, r, c, dr, dc):
        for i in range (len(dr)):
            tr = int(round(r+dr[i]))
            tc = int(round(c+dc[i]))
            if (tr < 0)or(tr > 14)or(tc < 0)or(tc > 14):
                return False
            v = state.board[tr][tc]
            if (v != turn):
                return False
        return True
    
    def getScore(self, state, r, c, turn, mode):
        #以下為遊戲相關資料與函數
        zero = [ 0, 0, 0, 0, 0]
        inc = [-2,-1, 0, 1, 2]
        dec = [ 2, 1, 0,-1,-2]
        z9 = [ 0, 0, 0, 0, 0, 0, 0, 0, 0]
        i9 = [-4,-3,-2,-1, 0, 1, 2, 3, 4]
        d9 = [ 4, 3, 2, 1, 0, -1, -2, -3, -4]
        z5 = [ 0, 0, 0, 0, 0]
        i2 = [-2, -1, 0, 1, 2]
        d2 = [2, 1, 0,-1,-2]
        attackScores = [0, 3, 10, 30, 100, 500]
        guardScores = [0, 2, 9, 25, 90, 400]
        score = 0
        if mode == 1:
            mScores = attackScores
        else:
            mScores = guardScores
        
        state.board[r][c] = turn;
        for start in range (5):
            for len in range (5, 0, -1):
                end = start+len
                zero = z9[start: start+len]
                inc = i9[start: start+len]
                dec = d9[start: start+len]
                if (state.patternCheck(state, turn, r, c, zero, inc)): # 攻擊：垂直 |
                    score += mScores[len]
                if (state.patternCheck(state, turn, r, c, inc, zero)): # 攻擊：水平 -
                    score += mScores[len]
                if (state.patternCheck(state, turn, r, c, inc, inc)): # 攻擊：下斜 \
                    score += mScores[len]
                if (state.patternCheck(state, turn, r, c, inc, dec)): # 攻擊：上斜 /
                    score += mScores[len]
        state.board[r][c] = 0  
        return score
    
    def computerTurn(self, state):
        bestR = 0
        bestC = 0
        bestScore = -1
        attack = 1
        guard = 2
        AI = 2
        player = 1
        
        for r in range(15):
            for c in range(15):
                if (state.board[r][c] != 0):
                    continue;
                attackScore = state.getScore(state, r, c, AI, attack)#攻擊分數
                guardScore  = state.getScore(state, r, c, player, guard)#防守分數
                score = attackScore+guardScore;
                if (score > bestScore):
                    bestR = r
                    bestC = c
                    bestScore = score
        
        m = [bestR, bestC]
        if (bestR >= 2)and(bestR <= 12)and(bestC >= 2)and(bestC <= 12):
            around = 0
            for i in range (bestR-2, bestR+3):
                for j in range (bestC-2, bestC+3):
                    around += state.board[i, j]
            if around == 3:
                return False
        print "ComputeScore"
        print "Move: " + str(m) + "\n"
        state.DoMove(m)
        state.steps.append(m)
        return True
        
    def _make_move(self, state):
        if self.win_if_possible(state): return
        if self.block_open_four(state): return
        if self.extend_three_to_doubly_open_four(state): return
        if self.extend_three_to_four(state): return
        if self.block_to_doubly_open_four(state): return
        if self.block_doubly_open_three(state): return
        if self.block_twice_to_three_or_more(state): return
        # if self.block_twice_to_four(state): return
        # if self.block_twice_to_three(state): return
        return False
    
    def _make_move_last(self, state):
        if self.block_open_three(state): return
        if self.extend_twice_two_to_three(state): return
        if self.block_doubly_open_two(state): return
        if self.block_open_two(state): return
        if self.extend_two_to_three(state): return
        if self.extend_one(state): return
        if self.sequential_move(state): return
        if self.random_move(state): return
        return False

class Node:
    # A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
    # Crashes if state not specified.
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves() # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        self.state = state.Clone()
        
    def UCTSelectChild(self):
        # Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
        # lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
        # exploration versus exploitation.
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits) + 10*c.state.GetScore(c.move))[-1]
        #print s.wins/s.visits, sqrt(2*log(self.visits)/s.visits), 5*s.state.GetScore(s.move)
        return s
    
    def AddChild(self, m, s):
        # Remove m from untriedMoves and add a new child node for this move.
        # Return the added child node
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        # Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range (1, indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s

def UCT(rootstate, itermax, verbose = False):
    # Conduct a UCT search for itermax iterations starting from rootstate.
    # Return the best move from the rootstate.
    # Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0].
    rootnode = Node(state = rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves) 
            state.DoMove(m)
            node = node.AddChild(m, state) # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != [] and state.winner == 0:  # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode
        
    # Output some information about the tree - can be omitted
    #if (verbose): print rootnode.TreeToString(0)
    #else: print rootnode.ChildrenToString()

    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited
                
def UCTPlayGame():
    # Play a sample game between two UCT players where each player gets a different number 
    # of UCT iterations (= simulations = tree nodes).
    state = Gomoku()
    
    # deal with the invalid input
    first = 0
    while (first != 1 and first != 2):
        first = input("Please decide which mode to play.\nMode 1: player first.\nMode 2: computer first.\n")
    state.SetFirst(first)

    # deal with the situation that computer first
    if state.playerJustMoved == 1:
        m = [7, 7]
        print "\nfirstStep"
        print "Move: " + str(m) + "\n"
        state.DoMove(m)
        state.steps.append(m)
        print str(state)
    
    while (state.GetMoves() != []):
        if state.playerJustMoved == 1:
            ticks1 = time.time()
            if (state.playerStepCount == 1)and(first == 1):
                if (m[0] <= 7)and(m[1] <= 7):
                    m = [m[0]+1, m[1]+1]
                elif (m[0] >= 7)and(m[1] <= 7):
                    m = [m[0]-1, m[1]+1]
                elif (m[0] <= 7)and(m[1] >= 7):
                    m = [m[0]+1, m[1]-1]
                else:
                    m = [m[0]-1, m[1]-1]
                print "playerStepCount"
                print "Move: " + str(m) + "\n"
                state.DoMove(m)
                state.steps.append(m)
            elif ((state.playerStepCount == 2)and((abs(m[0]-state.steps[0][0]) >= 3)or(abs(m[1]-state.steps[0][1]) >= 3))and(first == 1)) \
                or((state.playerStepCount == 1)and(first == 2)):
                state._make_move_last(state)
            elif state._make_move(state) == False:
                # play with values for itermax and verbose = True
                m = UCT(rootstate = state, itermax = 430, verbose = False)
                print "MCTS choose " + str(m)
                
                beginR = m[0]-2
                endR = m[0]+3
                beginC = m[1]-2
                endC = m[1]+3
                if beginR <= 0:
                    beginR = 0
                if endR >= 15:
                    endR = 15
                if beginC <= 0:
                    beginC = 0
                if endC >= 15:
                    endC = 15
                wrong = 1
                for i in range (beginR, endR):
                    for j in range (beginC, endC):
                        if (state.board[i, j] == 2):
                            if (m[0]-1 >= 0)and(m[1]+2 <= 14):
                                if (i == m[0]-1)and(j == m[1]+2): continue
                            if (m[0]+1 <= 14)and(m[1]+2 <= 14):
                                if (i == m[0]+1)and(j == m[1]+2): continue
                            if (m[0]-2 >= 0)and(m[1]+1 <= 14):
                                if (i == m[0]-2)and(j == m[1]+1): continue
                            if (m[0]+2 <= 14)and(m[1]+1 <= 14):
                                if (i == m[0]+2)and(j == m[1]+1): continue
                            if (m[0]-2 >= 0)and(m[1]-1 >= 0):
                                if (i == m[0]-2)and(j == m[1]-1): continue
                            if (m[0]+2 <= 14)and(m[1]-1 >= 0):
                                if (i == m[0]+2)and(j == m[1]-1): continue
                            if (m[0]-1 >= 0)and(m[1]-2 >= 0):
                                if (i == m[0]-1)and(j == m[1]-2): continue
                            if (m[0]+1 <= 14)and(m[1]-2 >= 0):
                                if (i == m[0]+1)and(j == m[1]-2): continue
                            wrong = 0
                            break
                    if wrong == 0: break                        
                if wrong == 0:
                    print "MCTS"
                    print "Move: " + str(m) + "\n"
                    state.DoMove(m)
                    state.steps.append(m)
                elif state.computerTurn(state) == False:
                    state._make_move_last(state)
            ticks2 = time.time()
            print "spend time: " + str(ticks2-ticks1) + "s\n" 
        else:
            state.playerStepCount += 1
            m = [-20, -20]
            invalid = 1
            while (invalid == 1):
                if state.winner != 0:
                    endGame = raw_input("Game Over? \n")
                    while ((endGame != "true")and(endGame != "false")):
                        endGame = raw_input("Game Over? \n")
                    if endGame == "true":
                        exit(0)
                           
                input_list = raw_input("Put your position: \n")
                
                if input_list == "undo":
                    state.Regret()
                    print "Regret!\n"
                    print str(state)
                else:
                    if(len(input_list) < 2):
                        invalid = 1
                        print "Invalid Input!"
                        continue
                    row = ord(input_list[0])-ord('A')
                    col = ord(input_list[1])-ord('0')
                    if len(input_list) == 3:
                        col = col*10+ord(input_list[2])-ord('0')
                    m = [row, col]
                    if (m[0] < 0) or (m[0] >= state.N) or (m[1] < 0) or (m[1] >= state.N):
                        invalid = 1
                        print "Invalid Input!"
                        continue
                    if state.board[m[0], m[1]] != 0:
                        invalid = 1
                        print "Invalid Input!"
                        continue
                    invalid = 0
            print "\nPlayer"
            print "Move: " + str(m) + "\n"
            state.DoMove(m)
            state.steps.append(m)
        
        print str(state)
        
        if state.winner != 0:
            if state.GetResult(state.playerJustMoved) == 1.0:
                print "Player " + str(state.playerJustMoved) + " wins!"
            elif state.GetResult(state.playerJustMoved) == 0.0:
                print "Player " + str(3 - state.playerJustMoved) + " wins!"
            else: print "Nobody wins!"

UCTPlayGame()