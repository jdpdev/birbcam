from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

previewResolution = (640, 480)

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

camera = PiCamera()
camera.resolution = previewResolution
camera.framerate = 32;
rawCapture = PiRGBArray(camera, size=previewResolution)

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    cv2.putText(image,"(E)xposure Mode: " + camera.exposure_mode,(20, 20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 0, 255),1)
    cv2.putText(image,"Shutter: %d" % camera.exposure_speed,(20, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 0, 255),1)
    cv2.putText(image,"(I)SO: %d" % camera.iso,(20, 60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 0, 255),1)
    cv2.putText(image,"(M)eter: " + camera.meter_mode,(20, 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 0, 255),1)

    (x, y, w, h) = get_meter_rect(camera.meter_mode)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)

    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)

    if key == ord("i"):
        if camera.iso == 800:
            camera.iso = 0
        else:
            camera.iso = camera.iso + 100

    if key == ord("e"):
        camera.exposure_mode = get_next_exposure(camera.exposure_mode)

    if key == ord("m"):
        camera.meter_mode = get_next_meter(camera.meter_mode)

    if key == ord("q"):
        break

# Closes all the frames
cv2.destroyAllWindows()