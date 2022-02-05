# Additional libs
import numpy as np
import cv2

def displayContours(gray):
    blank = np.zeros(gray.shape, dtype='uint8')
    cv2.imshow("blank", blank)

    ret, thresh = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)
    cv2.imshow("thresh", thresh)

    blur = cv2.GaussianBlur(gray, (5, 5), cv2.BORDER_DEFAULT)
    cv2.imshow("Blur", blur)

    canny = cv2.Canny(blur, 125, 175)
    cv2.imshow("Canny Edges", canny)

    contours, hierarchies = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    cv2.drawContours(blank, contours, -1, (0, 255, 0), 1)
    cv2.imshow("contours drawn", blank)