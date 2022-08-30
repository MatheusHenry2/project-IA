import numpy as np
from random import randint
from time import sleep
from os import system, name
import logging
import numpy as np

logging.basicConfig(
    level=logging.DEBUG,
    filename='mylog.log',
    filemode='w'
)


SPEED = 4
SLEEP = 1/SPEED

LEVEL_WIDTH = 70
LEVEL_HEIGHT = 30
WALL_PROBABILITY = 1
GARBAGE_PROBABILITY = 10

# Caso tenha algum problema com a renderização da simulação, use letras no lugar de códigos unicode;
# https://www.utf8icons.com/character/9608/full-block
WALL = '\u2588'
GARBAGE = '\u2237'
HOME = 'H'
LEFT = '\u25C0'
DOWN = '\u25BC'
RIGHT = '\u25B6'
UP = '\u25B2'
EMPTY = ' '
PICK_UP = 1
DISCARD = 2

P1_COLOR = '\033[95m'
P2_COLOR = '\033[94m'
P3_COLOR = '\033[96m'
P4_COLOR = '\033[92m'
P5_COLOR = '\033[93m'
P6_COLOR = '\033[91m'
P7_COLOR = '\033[1m'
P8_COLOR = '\033[4m'
NO_COLOR = '\033[0m'


class Level:
    def __init__(self, width, height, wprob, gprob):
        self.clear()
        self.width = width
        self.height = height
        self.level = []
        self.agents = []
        for y in range(0, height):
            coll = []
            for x in range(0, width):
                if x == 0 or x == (width - 1) or y == 0 or y == (height - 1):
                    coll.append(WALL)
                elif randint(0, 100) <= wprob:
                    coll.append(WALL)
                elif randint(0, 100) <= gprob:
                    coll.append(GARBAGE)
                else:
                    coll.append(EMPTY)

            self.level.append(coll)

    def gotoxy(self, x, y):
        print("%c[%d;%df" % (0x1B, y, x), end='')

    def printScore(self, agent):
        self.gotoxy(1, (self.height + agent.id + 2))
        print("P1-" + str((agent.id + 1)), agent.dir, ": ", agent.score)

    def clear(self):
        if name == 'nt':
            system('cls')
        else:
            system('clear')

    def addAgent(self, agent):
        while (True):
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)

            if self.level[y][x] in (EMPTY, GARBAGE):
                self.level[y][x] = HOME
                agent.Start(x, y, self.level, len(self.agents))
                agent.Draw()
                break

        self.agents.append(agent)

    def run(self):
        while (True):
            for agent in self.agents:
                agent.Update()

            self.draw()
            for agent in self.agents:
                agent.Draw()
                self.printScore(agent)

            sleep(SLEEP)

    def draw(self):
        self.gotoxy(0, 0)
        for y in range(0, self.height):
            for x in range(0, self.width):
                print(self.level[y][x], end="")
            print("")


class VacuumCleanerAgent:
    def __init__(self, brain, color):
        self.x = 0
        self.y = 0
        self.dir = UP
        self.color = color
        self.score = 0
        self.full = False
        self.brain = brain

    def Start(self, x, y, level, uid):
        self.x = x
        self.y = y
        self.level = level
        self.id = uid

    def Move(self, direction):
        sx = self.x
        sy = self.y

        if (direction == UP):
            sy -= 1
        elif (direction == DOWN):
            sy += 1
        elif (direction == LEFT):
            sx -= 1
        elif (direction == RIGHT):
            sx += 1
        else:
            return

        if (self.level[sy][sx] in (EMPTY, HOME, GARBAGE)):
            self.dir = self.color + direction + NO_COLOR
            self.x = sx
            self.y = sy

    def Draw(self):
        print("%c[%d;%df" % (0x1B, self.y+1, self.x+1), end='')
        print(self.dir)

    def Update(self):
        px = self.x
        py = self.y

        perception = [
            [self.level[py - 1][px - 1], self.level[py - 1]
                [px], self.level[py - 1][px + 1]],
            [self.level[py][px - 1], self.level[py][px], self.level[py][px + 1]],
            [self.level[py + 1][px - 1], self.level[py + 1]
                [px], self.level[py + 1][px + 1]]
        ]
   
        action = self.brain.NextAction(perception)
        if (action == PICK_UP):
            if (self.full == False and self.level[py][px] == GARBAGE):
                self.full = True
                self.level[py][px] = EMPTY
        elif (action == DISCARD):
            if (self.full == True and self.level[py][px] == HOME):
                self.full = False
                self.score += 1
        else:
            self.Move(action)


class Brain:
    def __init__(self):
        self.loaded = False

    mapa = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

    def NextAction(self, perception):

        # Percepções é uma matrix 3x3 com os dados que estão ao redor do VaccumCleaner
        # GARBAGE, WALL, EMPTY, HOME ou outro jogador (LEFT, UP, DOWN, RIGHT)

        # Lista de ações possíveis
        # UP, DOWN, LEFT, RIGHT, PICK_UP, DISCARD
        
        for i in self.mapa:
            logging.info(i)

        logging.info(' \n')

        if (perception[0][1] == EMPTY and perception[0][0] == EMPTY and perception[0][2] == EMPTY):
            self.mapa.insert(0, [EMPTY, EMPTY, EMPTY]) # - - -
        
        if (perception[0][1] == GARBAGE and perception[0][0] == GARBAGE and perception[0][2] == GARBAGE):
            self.mapa.insert(0, ['*', '*', '*']) # * * *
        
        if (perception[0][1] == WALL and perception[0][0] == WALL and perception[0][2] == WALL):
            self.mapa.insert(0, ['W', 'W', 'W']) # w w w

        if (perception[0][1] == EMPTY and perception[0][0] == EMPTY and perception[0][2] == WALL):
            self.mapa.insert(0, [EMPTY, EMPTY, 'W']) # - - w

        if (perception[0][1] == EMPTY and perception[0][0] == WALL and perception[0][2] == EMPTY):
            self.mapa.insert(0, [EMPTY, 'W', EMPTY]) # - w -

        if (perception[0][1] == WALL and perception[0][0] == EMPTY and perception[0][2] == EMPTY):
            self.mapa.insert(0, ['W', EMPTY, EMPTY]) # w - -


        if (perception[0][1] == GARBAGE and perception[0][0] == GARBAGE and perception[0][2] == EMPTY):
            self.mapa.insert(0, ['*', '*', EMPTY])

        if (perception[0][1] == GARBAGE and perception[0][0] == EMPTY and perception[0][2] == EMPTY):
            self.mapa.insert(0, ['*', EMPTY, EMPTY])

        return UP
        # if (perception[1][1] == GARBAGE):
        #     self.loaded = True
        #     return PICK_UP
        # elif (self.loaded):
        #     if (perception[1][1] == HOME):
        #         self.loaded = False
        #         return DISCARD
        #     else:
        #         return DOWN
        # return UP


class Brain2:
    def __init__(self):
        self.loaded = False

    def NextAction(self, perception):
        # Percepções é uma matrix 3x3 com os dados que estão ao redor do VaccumCleaner
        # GARBAGE, WALL, EMPTY, HOME ou outro jogador (LEFT, UP, DOWN, RIGHT)

        # Lista de ações possíveis
        # UP, DOWN, LEFT, RIGHT, PICK_UP, DISCARD
        if (perception[1][1] == GARBAGE):
            self.loaded = True
            return PICK_UP
        elif (self.loaded):
            if (perception[1][1] == HOME):
                self.loaded = False
                return DISCARD
            else:
                return LEFT
        return RIGHT


class Brain3:
    def __init__(self):
        self.loaded = False

    def NextAction(self, perception):
        # Percepções é uma matrix 3x3 com os dados que estão ao redor do VaccumCleaner
        # GARBAGE, WALL, EMPTY, HOME ou outro jogador (LEFT, UP, DOWN, RIGHT)

        # Lista de ações possíveis
        # UP, DOWN, LEFT, RIGHT, PICK_UP, DISCARD
        if (perception[1][1] == GARBAGE):
            self.loaded = True
            return PICK_UP
        elif (self.loaded):
            if (perception[1][1] == HOME):
                self.loaded = False
                return DISCARD
            else:
                return RIGHT
        return LEFT


class Brain4:
    def __init__(self):
        self.loaded = False

    def NextAction(self, perception):
        # Percepções é uma matrix 3x3 com os dados que estão ao redor do VaccumCleaner
        # GARBAGE, WALL, EMPTY, HOME ou outro jogador (LEFT, UP, DOWN, RIGHT)

        # Lista de ações possíveis
        # UP, DOWN, LEFT, RIGHT, PICK_UP, DISCARD
        if (perception[1][1] == GARBAGE):
            self.loaded = True
            return PICK_UP
        elif (self.loaded):
            if (perception[1][1] == HOME):
                self.loaded = False
                return DISCARD
            else:
                return UP
        return DOWN


level = Level(LEVEL_WIDTH, LEVEL_HEIGHT, WALL_PROBABILITY, GARBAGE_PROBABILITY)
level.addAgent(VacuumCleanerAgent(Brain(), P1_COLOR))
level.addAgent(VacuumCleanerAgent(Brain2(), P2_COLOR))
level.addAgent(VacuumCleanerAgent(Brain3(), P3_COLOR))
level.addAgent(VacuumCleanerAgent(Brain4(), P4_COLOR))
level.run()
