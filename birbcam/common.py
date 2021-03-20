import cv2
import imutils
import numpy as np

def draw_mask(image, mask, resolution):
    (x, y, w, h) = mask

    maskOverlay = image.copy()

    left = int(resolution[0] * x)
    right = left + int(resolution[0] * w)
    top = int(resolution[1] * y)
    bottom = top + int(resolution[1] * h)

    cv2.rectangle(maskOverlay, (0,0), (resolution[0],top), (0,0,0), -1)
    cv2.rectangle(maskOverlay, (0,bottom), (resolution[0],resolution[1]), (0,0,0), -1)
    cv2.rectangle(maskOverlay, (0,0), (left,resolution[1]), (0,0,0), -1)
    cv2.rectangle(maskOverlay, (right,0), (resolution[0],resolution[1]), (0,0,0), -1)

    cv2.addWeighted(maskOverlay, 0.7, image, 0.3, 0, image)
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 255), 1)

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

def change_mask_size(x, y, resolution):
    width = resolution[0]
    height = resolution[1]
    cx = int(width / 2)
    cy = int(height / 2)
    dx = cx - x
    dy = cy - y
    mx = abs(dx / width) * 2
    my = abs(dy / height) * 2

    return (mx, my)

def get_mask_real_size(mask, resolution):
    (x, y, w, h) = mask
    return (int(resolution[0] * w), int(resolution[1] * h))

def get_mask_coords(mask, resolution):
    (x, y, w, h) = mask
    return {
        "tl": {
            "x": int(x * resolution[0]), 
            "y": int(y * resolution[1])
        },
        "br": {
            "x": int(x * resolution[0]) + int(w * resolution[0]), 
            "y": int(y * resolution[1]) + int(h * resolution[1])
        }
    }

def extract_image_region(image, bounds):
    return image[bounds["tl"]["y"]:bounds["br"]["y"], bounds["tl"]["x"]:bounds["br"]["x"]]

def draw_aim_grid(image, resolution):
    x0 = 0
    x1 = int(resolution[0] / 3)
    x2 = int(resolution[0] / 3) * 2
    x3 = resolution[0]
    xc = int(resolution[0] / 2)
    y0 = 0
    y1 = int(resolution[1] / 3)
    y2 = int(resolution[1] / 3) * 2
    y3 = resolution[1]
    yc = int(resolution[1] / 2)
    w = 1
    c = (255, 0, 255)
    cc = (255, 255, 0)

    cv2.line(image, (x0, y1), (x3, y1), c, w)
    cv2.line(image, (x0, y2), (x3, y2), c, w)
    cv2.line(image, (x1, y0), (x1, y3), c, w)
    cv2.line(image, (x2, y0), (x2, y3), c, w)
    cv2.line(image, (x0, yc), (x3, yc), cc, w)
    cv2.line(image, (xc, y0), (xc, y3), cc, w)