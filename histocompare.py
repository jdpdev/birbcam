from common import draw_mask
from time import time, sleep
import cv2
import numpy as np
import imutils
import argparse

def reduce_img(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    gray = imutils.resize(gray, width=800)
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

def compare_histograms(a, b):
    compare = cv2.compareHist(a, b, cv2.HISTCMP_CHISQR)
    return compare

aimg = cv2.imread("/home/pi/Public/birbs/2021-01-22-11:02:44.jpg")
bimg = cv2.imread("/home/pi/Public/birbs/2021-01-22-11:02:33.jpg")
cimg = cv2.imread("/home/pi/Public/birbs/2021-01-22-11:02:21.jpg")

aimg = reduce_img(aimg)
bimg = reduce_img(bimg)
cimg = reduce_img(cimg)
delta = cv2.absdiff(aimg, cimg)

(ahist, adata) = build_histogram(aimg)
(bhist, bdata) = build_histogram(cimg)
ahistimg = draw_histogram(adata)
bhistimg = draw_histogram(bdata)
comparison = compare_histograms(ahist, bhist)

blank = np.zeros((600,800,1), np.uint8)

left = cv2.hconcat([ahistimg, bhistimg])
left = cv2.resize(left, (800, 300))
delta = cv2.resize(delta, (400, 300))
#quad = cv2.hconcat([left, right])
#quad = cv2.resize(quad, (800, 600))

#cv2.imshow('blank', delta)
#cv2.imshow('breakdown', quad)
#cv2.imshow('ahist', ahistimg)
#cv2.imshow('bhist', bhistimg)
cv2.imshow('histograms', left)
cv2.imshow('delta', delta)
print("Comparison: ", comparison)

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()