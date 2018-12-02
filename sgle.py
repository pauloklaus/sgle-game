#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SGLE|SuperGravitronLeetEdition*
# Pwn2Win2018
# author: pauloklaus@tutanota.com
# greetz: alisson@bertochi.com.br, watsonmaster@gmail.com, marlon.d@outlook.com

import curses
from curses import KEY_RIGHT, KEY_LEFT
from random import randint
import time
import locale

locale.setlocale(locale.LC_ALL, '')

WIDTH = 30
HEIGHT = 10
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
JUMPER_REFRESH = 0.03
BULLET_REFRESH = 0.05
TARGET_TIME = 137
FLAG = "[xxFLAGxx]"

KEY_ESC = 27
KEY_Q1 = 81
KEY_Q2 = 113
KEY_ENTER = 10
KEY_SPACE = 32

class Jumper(object):
    def __init__(self, window, char='I'):
        self.window = window
        self.char = char
        self.x = MAX_X / 2
        self.y = MAX_Y / 2
        self.updown = 1
        self.start_time = time.time()

        self.direction = KEY_LEFT
        self.direction_map = {
            KEY_LEFT: self.move_left,
            KEY_RIGHT: self.move_right
        }

    def render(self):
        self.window.addstr(0, 1, "[{}:{}]".format(self.y, self.x))
        self.window.addstr(self.y, self.x, self.char)

    def update(self):
        elapsed_time = time.time() - self.start_time

        if elapsed_time < JUMPER_REFRESH:
            return

        self.start_time = time.time()

        if self.y == MAX_Y:
            self.updown = 0

        if self.y == 1:
            self.updown = 1

        if self.updown:
            self.y += 1
        else:
            self.y -= 1

        self.direction_map[self.direction]()

    def change_direction(self, direction):
        self.direction = direction

    def move_left(self):
        self.x -= 1
        if self.x < 1:
            self.x = MAX_X

    def move_right(self):
        self.x += 1
        if self.x > MAX_X:
            self.x = 1

    @property
    def getx(self):
        return self.x

    @property
    def gety(self):
        return self.y

class Bullet(object):
    CHAR = ['*', '>', '=', '+']

    def __init__(self, window, y, x):
        self.window = window
        self.y_init = y
        self.x_init = x
        self.dir_init = (x < 1)
        self.start()

    def start(self):
        self.ended = False
        self.start_time = time.time()
        self.y = self.y_init
        self.x = self.x_init
        self.dir = self.dir_init
        self.char = self.CHAR[randint(0, len(self.CHAR) - 1)]

    def update(self):
        if time.time() - self.start_time < BULLET_REFRESH:
            return self.ended

        self.start_time = time.time()

        if self.dir:
            self.ended = self.x > MAX_X
            if not self.ended:
                self.x += 1
        else:
            self.ended = self.x < 1
            if not self.ended:
                self.x -= 1

        return self.ended

    def blast(self):
        char = "X****"

        self.window.addstr(self.y, self.x, char[0])

        if self.y - 1 > 0:
            self.window.addstr(self.y - 1, self.x, char[1])

        if self.x + 1 <= MAX_X:
            self.window.addstr(self.y, self.x + 1, char[2])

        if self.y + 1 <= MAX_Y:
            self.window.addstr(self.y + 1, self.x, char[3])

        if self.x - 1 > 0:
            self.window.addstr(self.y, self.x - 1, char[4])

    def collided(self, y, x):
        done = self.y == y and self.x == x

        if done:
            self.blast()

        return done

    def render(self):
        if self.x > 0 and self.x <= MAX_X and not self.ended:
            self.window.addstr(self.y, self.x, self.char)

class BulletSet(object):
    def __init__(self, window, bullets):
        self.window = window
        self.bullets = []

        for bullet in bullets:
            self.bullets.append(Bullet(window, bullet[0], bullet[1]))

    def render(self):
        for bullet in self.bullets:
            bullet.render()

    def update(self):
        ended = True

        for bullet in self.bullets:
            bullet_ended = bullet.update()
            if not bullet_ended:
                ended = False

        return ended

    def collided(self, y, x):
        for bullet in self.bullets:
            if bullet.collided(y, x):
                return True

        return False;

    def restart(self):
        for bullet in self.bullets:
            bullet.start()

class GameBoard(object):
    def __init__(self, window, bulletsets):
        self.window = window
        self.bulletsets = []
        self.pointer = 0
        self.start_time = time.time()

        for bulletset in bulletsets:
            self.bulletsets.append(BulletSet(window, bulletset))

    def random_init(self):
        self.pointer = randint(0, len(self.bulletsets) - 1)

    def render(self):
        self.render_time()
        # step debug
        #self.window.addstr(0, 22, "[{}/{}]".format(self.pointer, len(self.bulletsets)))
        self.bulletsets[self.pointer].render()

    def render_time(self):
        self.window.addstr(0, 10, "[{0:.2f}]".format(time.time() - self.start_time))

    def update(self):
        if self.bulletsets[self.pointer].update():
            self.bulletsets[self.pointer].restart()

            self.pointer += 1
            if self.pointer >= len(self.bulletsets):
                self.pointer = 0

    def bye(self):
        key = -1
        while key not in [KEY_ENTER, KEY_ESC, KEY_SPACE, KEY_Q1, KEY_Q2]:
            key = window.getch()

    def collided(self, y, x):
        if self.bulletsets[self.pointer].collided(y, x):
            self.bye()
            return True

        return False

    def time_achieved(self):
        if time.time() - self.start_time < TARGET_TIME:
            return False

        self.render_time()
        self.window.addstr(MAX_Y + 1, 1, FLAG)
        self.bye()

        return True

if __name__ == '__main__':
    curses.initscr()
    window = curses.newwin(HEIGHT, WIDTH, 0, 0)
    window.timeout(20)
    window.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    window.border(0)

    bsTopLeft2 = [[2,0], [5,-6]]
    bsBottomRight2 = [[7,MAX_X], [4,MAX_X+6]]
    bsLeftRight4 = bsTopLeft2 + bsBottomRight2

    bsTopLeft3 = [[2,0], [5,-6], [3,-12]]
    bsBottomRight3 = [[7,MAX_X], [4,MAX_X+6], [6,MAX_X+12]]
    bsLeftRight6 = bsTopLeft3 + bsBottomRight3

    bsLeftWall3 = [[2,0], [4,0], [6,0]]
    bsRightWall3 = [[8,MAX_X], [6,MAX_X], [4,MAX_X]]
    bsLeftRightWall6 = bsLeftWall3 + bsRightWall3

    bsLeftTopBottom2 = [[1,0], [8,0]]
    bsRightMiddle2 = [[4,MAX_X], [5,MAX_X]]
    bsLeftTopBottomRightMiddle4 = bsLeftTopBottom2 + bsRightMiddle2

    bsRightTopBottom2 = [[1,MAX_X], [8,MAX_X]]
    bsLeftMiddle2 = [[4,0], [5,0]]
    bsRightTopBottomLeftMiddle4 = bsRightTopBottom2 + bsLeftMiddle2

    bsLeftTopBottom4 = [[1,0], [3,-5], [8,0], [5,-5]]
    bsRightMiddle4 = [[4,MAX_X], [5,MAX_X], [2,MAX_X+5], [7,MAX_X+5]]
    bsLeftTopBottomRightMiddle8 = bsLeftTopBottom4 + bsRightMiddle4

    bsRightTopBottom4 = [[1,MAX_X], [3,MAX_X+5], [8,MAX_X], [5,MAX_X+5]]
    bsLeftMiddle4 = [[4,0], [5,0], [2,-5], [7,-5]]
    bsRightTopBottomLeftMiddle8 = bsLeftTopBottom4 + bsRightMiddle4

    bsLeftMiddleBlock8 = [[3,-1], [4,-2], [4,-1], [4,0], [5,-2], [5,-1], [5,0], [6,-1]]
    bsLeftMiddleBlockRightTopBottom10 = bsLeftMiddleBlock8 + bsRightTopBottom2

    bsRightMiddleBlock8 = [[3,MAX_X+1], [4,MAX_X+2], [4,MAX_X+1], [4,MAX_X], [5,MAX_X+2], [5,MAX_X+1], [5,MAX_X], [6,MAX_X+1]]
    bsRightMiddleBlockLeftTopBottom10 = bsRightMiddleBlock8 + bsLeftTopBottom2

    jumper = Jumper(window)
    gameboard = GameBoard(window, [
        bsTopLeft2,
        bsRightTopBottom2,
        bsBottomRight2,
        bsLeftMiddle2,
        bsLeftRight4,
        bsRightTopBottomLeftMiddle4,
        bsTopLeft3,
        bsLeftTopBottom4,
        bsBottomRight3,
        bsRightMiddle4,
        bsLeftRight6,
        bsLeftTopBottomRightMiddle8,
        bsLeftWall3,
        bsRightTopBottom4,
        bsRightWall3,
        bsLeftMiddle4,
        bsLeftRightWall6,
        bsRightTopBottomLeftMiddle8,
        bsLeftTopBottom2,
        bsLeftMiddleBlock8,
        bsRightMiddle2,
        bsLeftMiddleBlockRightTopBottom10,
        bsLeftTopBottomRightMiddle4,
        bsRightMiddleBlock8,
        bsRightMiddleBlockLeftTopBottom10,
    ])

    while True:
        window.clear()
        window.border()

        jumper.render()
        gameboard.render()

        event = window.getch()

        if event in [KEY_LEFT, KEY_RIGHT]:
            jumper.change_direction(event)

        if event in [KEY_ESC, KEY_Q1, KEY_Q2]:
            break

        if gameboard.collided(jumper.gety, jumper.getx):
            break

        if gameboard.time_achieved():
            break

        jumper.update()
        gameboard.update()

    curses.endwin()
