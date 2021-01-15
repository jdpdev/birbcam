import cv2

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