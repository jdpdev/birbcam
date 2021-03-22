from picamerax.array import PiRGBArray
from picamerax import PiCamera
from time import sleep
#import lensshading
import sys
import logging
from setproctitle import setproctitle

from .birbconfig import BirbConfig
from .focusassist import FocusAssist
from .imagemask import ImageMask
from .birbwatcher import BirbWatcher

previewResolution = (640, 480)

def run_birbcam():
    setproctitle("birbcam")
    config = BirbConfig()

    if not config.logFile is None:
        logging.basicConfig(level=logging.INFO, filename=config.logFile, format='(%(asctime)s) %(levelname)s: %(message)s', datefmt="%H:%M:%S")
    else:
        logging.basicConfig(level=logging.INFO, format='(%(asctime)s) %(levelname)s: %(message)s', datefmt="%H:%M:%S")

    logging.info(f"Saving output to: {config.saveTo}")
    if config.noCaptureMode: logging.info("Using No Capture Mode")
    if config.debugMode: logging.info("Using Debug Mode")

    camera = PiCamera()
    camera.resolution = previewResolution
    camera.framerate = 30;
    camera.iso = 200
    rawCapture = PiRGBArray(camera, size=previewResolution) 

    """
    shading = lensshading.get_lens_shading(args.get("lensshading"))
    if shading != None:
        shading = shading.astype("uint8")
        print(np.shape(shading))
        camera.lens_shading_table = shading
    """

    camera.exposure_mode = 'auto'
    camera.awb_mode = 'auto'
    camera.meter_mode = 'spot'

    sleep(2)

    camera.shutter_speed = camera.exposure_speed

    # **************************************
    #   Focus assist
    # **************************************
    focusAssist = FocusAssist()
    if focusAssist.run(camera) == False: sys.exit()

    # **************************************
    #   Set mask
    # **************************************
    imageMask = ImageMask()
    if imageMask.run(camera) == False: sys.exit()
    mask = imageMask.mask

    # **************************************
    #   Capture loop
    # **************************************
    watcher = BirbWatcher(config)
    watcher.run(camera, mask)