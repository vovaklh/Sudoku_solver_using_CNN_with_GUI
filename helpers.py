from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
import numpy as np
import cv2
import imutils


def find_board(image, debug=False):
    # convert image to grayscale and blur it
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 3)

    # apply adaptive threshodling
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.bitwise_not(thresh)

    # find contours
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    # points of board
    boardCnt = None

    # loop over contours
    for cnt in cnts:
        # approximate the contour
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # we assume that the board has four points
        if len(approx) == 4:
            boardCnt = approx
            break

    # if we didn't find board
    if boardCnt is None:
        raise Exception("Board has not been found")

    # apply four-point transform to original and gray image
    board = four_point_transform(image, boardCnt.reshape(4, 2))
    warped = four_point_transform(gray, boardCnt.reshape(4, 2))

    return board, warped


def extract_digit(cell, debug=False):
    # apply automatic thresholding to the cell and then clear any
    # connected borders that touch the border of the cell
    thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh = clear_border(thresh)


    # find contours in cell
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    if len(cnts) == 0:
        return None

    # if contour is not empty
    c = max(cnts, key=cv2.contourArea)
    mask = np.zeros(thresh.shape, dtype="uint8")
    cv2.drawContours(mask, [c], -1, 255, -1)

    # compute the percentage of masked pixels relative to the total
    # area of the image
    (h, w) = thresh.shape
    percentFilled = cv2.countNonZero(mask) / float(w * h)

    if percentFilled < 0.03:
        return None

    # apply mask to threshold cell
    digit = cv2.bitwise_and(thresh, thresh, mask=mask)

    return digit
