import tensorflow as tf
import cv2
import numpy as np
from sudoku import Sudoku
import imutils
from helpers import find_board, extract_digit


def load_model(path):
    model = tf.keras.models.load_model(path)

    return model


def load_image(path):
    image = cv2.imread(path)

    if image.shape[1] > 600:
        image = imutils.resize(image, width=600)

    return image


def get_sudoku_board(model_path, image_path, debug=False):
    # load model
    model = load_model(model_path)

    # load image
    image = load_image(image_path)

    if debug:
        cv2.imshow("Image", image)
        cv2.waitKey(0)

    # find board in image
    board, warped = find_board(image)

    if debug:
        cv2.imshow("Board", board)
        cv2.waitKey(0)

    # initialize sudoku board
    sudoku_board = np.zeros((9, 9), dtype="int")

    # divide warped image into 9*9 grid
    stepX = warped.shape[1] // 9
    stepY = warped.shape[0] // 9

    # loop over grid loocation
    for y in range(0, 9):
        for x in range(0, 9):
            startX = x * stepX
            startY = y * stepY
            endX = (x + 1) * stepX
            endY = (y + 1) * stepY

            cell = warped[startY: endY, startX: endX]
            digit = extract_digit(cell)

            if digit is not None:
                roi = cv2.resize(digit, (28, 28))
                roi = roi.astype("float") / 255
                roi = tf.keras.preprocessing.image.img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)

                # make prediction
                pred = model.predict(roi).argmax(axis=1)[0]
                sudoku_board[y, x] = pred
    if debug:
        cv2.destroyAllWindows()

    return sudoku_board


def solve_sodoku(board):
    puzzle = Sudoku(3, 3, board=np.array(board).tolist())

    solution = puzzle.solve()

    return solution.board


def board_is_valid(board):
    puzzle = Sudoku(3, 3, board=np.array(board).tolist())
    solution = puzzle.solve()

    for i in solution.board:
        if None in i:
            return False

    return True


