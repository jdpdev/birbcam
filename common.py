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
    return (int(resolution[0] * mask[0]), int(resolution[1] * mask[1]))

def get_mask_coords(mask, resolution):
    size = get_mask_real_size(mask, resolution)
    halfSize = {"x": size[0] / 2, "y": size[1] / 2}
    halfRes = {"x": resolution[0] / 2, "y": resolution[1] / 2}
    return {
        "tl": {"x": int(halfRes["x"] - halfSize["x"]), "y": int(halfRes["y"] - halfSize["y"])},
        "br": {"x": int(halfRes["x"] + halfSize["x"]), "y": int(halfRes["y"] + halfSize["y"])}
    }

def extract_image_region(image, bounds):
    return image[bounds["tl"]["y"]:bounds["br"]["y"], bounds["tl"]["x"]:bounds["br"]["x"]]