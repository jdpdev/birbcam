from cv2 import cvtColor, calcHist, COLOR_BGR2GRAY
import numpy as np

def calculate_exposure(image):
    histogram = build_image_histogram(image)
    return calculate_exposure_from_histogram(histogram)

def build_image_histogram(image):
    histogram = calcHist([image], [0], None, [256], [0,255])
    data = np.int32(np.around(histogram))
    
    return data

def calculate_exposure_from_histogram(histogram):
    max = histogram.max()
    average = 0
    total = 0

    for x, y in enumerate(histogram):
        average += y * x
        total += y

    return int(average / total)
