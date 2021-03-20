from picamera.array import PiRGBArray
from picamera import PiCamera
from birbloop import BirbWatcher, setup_logging
from common import draw_mask
import time
import cv2
import numpy as np

previewResolution = (640, 480)
mask = (0.5, 0.5)
windowName = 'preview'

def get_next_exposure(exp):
    return get_next_enum(PiCamera.EXPOSURE_MODES, exp)

def get_next_meter(meter):
    return get_next_enum(PiCamera.METER_MODES, meter)

def get_next_enum(enum, exp):
    modes = list(enum)
    useNext = False

    for mode in modes:
        if useNext:
            return mode

        if mode == exp:
            useNext = True

    return modes[0]

def get_meter_rect(meter):
    width = previewResolution[0]
    height = previewResolution[1]
    halfW = width / 2
    halfH = height / 2

    modes = {
        "average": (int(halfW - halfW * 0.25), int(halfH - halfH * 0.25), int(width * 0.25), int(height * 0.25)),
        "spot": (int(halfW - halfW * 0.1), int(halfH - halfH * 0.1), int(width * 0.1), int(height * 0.1)),
        "backlit": (int(halfW - halfW * 0.3), int(halfH - halfH * 0.3), int(width * 0.3), int(height * 0.3)),
        "matrix": (0, 0, width, height)
    }

    return modes[meter]

def mask_expand_horizontal(size):
    x = size[0]
    if x < 1:
        x += 0.05
    return (x, size[1])

def mask_contract_horizontal(size):
    x = size[0]
    if x > 0:
        x -= 0.05
    return (x, size[1])

def mask_expand_vertical(size):
    y = size[1]
    if y < 1:
        y += 0.05
    return (size[0], y)

def mask_contract_vertical(size):
    y = size[1]
    if y > 0:
        y -= 0.05
    return (size[0], y)

def click_size_mask(event, x, y, flags, param):
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    print("left mouse down: ", x, ", ", y)

    width = previewResolution[0]
    height = previewResolution[1]
    cx = int(width / 2)
    cy = int(height / 2)
    print("  ", cx, ", ", cy)
    dx = cx - x
    dy = cy - y
    print("  ", dx, ", ", dy)
    mx = abs(dx / width) * 2
    my = abs(dy / height) * 2
    print("  ", mx, ", ", my)

    global mask
    mask = (mx, my)

cv2.namedWindow(windowName)
cv2.setMouseCallback(windowName, click_size_mask)

camera = PiCamera()
camera.resolution = previewResolution
camera.framerate = 32;
rawCapture = PiRGBArray(camera, size=previewResolution)

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    draw_mask(image, mask, previewResolution)

    cv2.putText(image,"(E)xposure Mode: " + camera.exposure_mode,(20, 20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),1)
    cv2.putText(image,"Shutter: %d" % camera.exposure_speed,(20, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),1)
    cv2.putText(image,"(I)SO: %d" % camera.iso,(20, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),1)
    cv2.putText(image,"Meter: " + camera.meter_mode,(20, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),1)

    (x, y, w, h) = get_meter_rect(camera.meter_mode)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)

    cv2.imshow(windowName, image)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)

    if key == ord("i"):
        if camera.iso == 800:
            camera.iso = 0
        else:
            camera.iso = camera.iso + 100

    if key == ord("e"):
        camera.exposure_mode = get_next_exposure(camera.exposure_mode)

    #if key == ord("m"):
    #    camera.meter_mode = get_next_meter(camera.meter_mode)

    if key == ord("v"):
        mask = mask_contract_horizontal(mask)

    if key == ord("b"):
        mask = mask_expand_horizontal(mask)

    if key == ord("n"):
        mask = mask_contract_vertical(mask)

    if key == ord("m"):
        mask = mask_expand_vertical(mask)

    if key == ord("q"):
        break

# Closes all the frames
cv2.destroyAllWindows()
camera.close()

watcher = BirbWatcher(mask)
watcher.run()