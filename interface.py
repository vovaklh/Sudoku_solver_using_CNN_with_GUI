import pygame
import argparse
from solver import get_sudoku_board, solve_sodoku, board_is_valid
import os
import numpy as np
from tkinter import *
from tkinter import messagebox

# construct parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True)
ap.add_argument("-m", "--model", default="Resources/models/model.h5")
ap.add_argument("-d", "--debug", type=int, default=-1)
args = vars(ap.parse_args())

pygame.font.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'


class Grid:
    board = get_sudoku_board(args['model'], args['image'], args['debug'] > 0)

    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.selected = None
        self.solution = list(np.zeros((rows, cols)))

    # set value of cube
    def sketch(self, val):
        row, col = self.selected
        if self.cubes[row][col].value != 0:
            self.cubes[row][col].set(val)

    def part_of_solution(self):
        row, col = self.selected

        self.cubes[row][col].set(self.solution[row][col])

    def draw(self, win):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0, 0, 0), (0, i * gap), (self.width, i * gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def show_full_solution(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].set(self.solution[i][j])

    def get_solution(self):
        self.solution = solve_sodoku(self.cubes_to_array())

    def is_valid(self):
        return board_is_valid(self.cubes_to_array())

    def cubes_to_array(self):
        arr = []
        for i in range(self.rows):
            temp = []
            for j in range(self.cols):
                temp.append(self.cubes[i][j].get())
            arr.append(temp)

        return arr

    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return int(y), int(x)
        else:
            return None


class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if not (self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))

        # draw rectangle around cube
        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def get(self):
        return self.value


def redraw_window(win, board, strikes):
    win.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)

    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw(win)


def main():
    win = pygame.display.set_mode((540, 600))
    pygame.display.set_caption("Sudoku")
    board = Grid(9, 9, 540, 540)
    key = None
    flag = True
    run = True
    strikes = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if flag:
                    if event.key == pygame.K_1:
                        key = 1
                    if event.key == pygame.K_2:
                        key = 2
                    if event.key == pygame.K_3:
                        key = 3
                    if event.key == pygame.K_4:
                        key = 4
                    if event.key == pygame.K_5:
                        key = 5
                    if event.key == pygame.K_6:
                        key = 6
                    if event.key == pygame.K_7:
                        key = 7
                    if event.key == pygame.K_8:
                        key = 8
                    if event.key == pygame.K_9:
                        key = 9
                    if event.key == pygame.K_r:
                        if board.is_valid():
                            board.get_solution()
                            flag = False
                        else:
                            window = Tk()
                            window.wm_withdraw()
                            messagebox.showerror("Error", "Board is incorrect")
                            window.destroy()
                            window.quit()

                elif not flag:
                    if event.key == pygame.K_s:
                        board.show_full_solution()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key and flag:
            board.sketch(key)

        elif board.selected and not flag:
            board.part_of_solution()

        redraw_window(win, board, strikes)
        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit()
