import cv2
import imutils
import numpy as np

def draw_mask(image, mask, resolution):
    halfRes = (int(resolution[0] / 2), int(resolution[1] / 2))
    maskRes = (int((resolution[0] * mask[0]) / 2), int((resolution[1] * mask[1]) / 2))

    left = halfRes[0] - maskRes[0]
    right = halfRes[0] + maskRes[0]
    top = halfRes[1] - maskRes[1]
    bottom = halfRes[1] + maskRes[1]

    cv2.rectangle(image, (0,0), (resolution[0],top), (0,0,0), -1)
    cv2.rectangle(image, (0,bottom), (resolution[0],resolution[1]), (0,0,0), -1)
    cv2.rectangle(image, (0,0), (left,resolution[1]), (0,0,0), -1)
    cv2.rectangle(image, (right,0), (resolution[0],resolution[1]), (0,0,0), -1)

def reduce_img(img, resize=None):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    if not resize is None:
        gray = imutils.resize(gray, width=resize)

    return gray

def build_histogram(a):
    hist = cv2.calcHist([a], [0], None, [256], [0,256])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    data = np.int32(np.around(hist))

    return (hist, data)

def draw_histogram(data):
    blank = np.zeros((600,800,1), np.uint8)

    for x, y in enumerate(data):
        cv2.line(blank, (x * 3,600),(x * 3,600-y*2),(255,255,255))

    return blank

# takes the direct output of calcHist
def compare_histograms(a, b):
    compare = cv2.compareHist(a, b, cv2.HISTCMP_CHISQR)
    return compare