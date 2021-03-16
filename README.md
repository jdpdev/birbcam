# birbcam

A Raspberry Pi-powered, change-activated camera for watching bird feeders.

Check out (Birbserver)[https://github.com/jdpdev/birbserver], a web interface for your Birbcam designed to run on the same RPI.

## Set Up
### Hardware

#### Required
* Raspberry Pi - All testing has been done on a [Raspberry Pi 4 Model-B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) with 4GB of RAM. If you're brand new to Raspberry Pi, there are many options for kits that come with the board, the OS pre-installed on a boot SD card, and a case.
* Raspberry Pi Camera
    * [Camera Module V2](https://www.raspberrypi.org/products/camera-module-v2/) - A small 8MP, fixed-focus camera. Lens is wide so will have to be mounted close to the feeder. Focus can be adjusted, but it is not really meant to be refocused. Good for testing, but if you stick with it you will want to upgrade to...
    * [HQ Camera](https://www.raspberrypi.org/products/raspberry-pi-high-quality-camera/) - 12MP, a much bigger sensor than the V2, and swappable lenses. Standard lenses come with 6mm and 16mm (28mm and 85mm equivalent on a 35mm camera) focal lengths; I find the 16mm to be a very good choice.

#### Good To Have
* [Adafruit HQ Camera Case](https://learn.adafruit.com/raspberry-pi-hq-camera-case) - Combines the RPI and HQ Camera in a handy package. Has to be 3D printed. The HQ camera has a integrated standard tripod screw mount.
* External USB Storage - Protects the boot SD card from degredation, and provides the convience of being able to plug into another computer to work on your pictures.
* Longer Lenses - [Arducam](https://www.arducam.com/product-category/lenses/) sells lenses for the HQ camera with longer focal lengths, but they require color correction that is not yet available in Birbcam.

### Environment

Requires the following Python packages, available on PIP
```
picamerax
opecv-python
numpy
imutils
```

### config.ini

Important settings are saved in the `config.ini` file; some can be overridden by CLI arguments when running the app. Defaults are provided, but some will require local configuration.

* `[Saving] Directory` - Where images taken by the camera are saved. It is suggested that you save to an external drive, rather than the SD card.
* `[Debug] Enable` - Debug mode provides a live interface for monitoring the camera. This is suggested as currently there is no other way to change the camera exposure.

#### TODO
* Add setting for configuring sensitivity of the detector
* Add setting for configuring full picture cooldown
* Add setting for configuring live picture cooldown

## Running
Run the app via the command line

```python3 birbcam.py```

### Focus Assist
The first screen that opens is a live view from the camera to help you aim the camera, and set the focus. 
The number in the top right is a relative, unit-less value that approximates how much of the image is in focus. Max focus corresponds to the largest value.

To select a specific area to focus, you can click and drag a rectangle to zoom. To reset the zoom press `R`.

To continue, press `Q`.
To exit the app, press `X`.

### Detector Mask
The second screen that opens is a live view from the camera to set the Detection Mask. 
When the camera is running, only changes to the image within the detection mask are used to trigger the taking of a picture.

To select a specific area to mask, you can click and drag with the mouse. The detection area is within the yellow rectangle.

To continue, press `Q`.
To exit the app, press `X`.

### Camera Watcher
If you are running Debug Mode, the final screen is the observing interface, which you can use to monitor the camera. There are four quadrants in the display:

![2021-02-23-12-13-53](https://user-images.githubusercontent.com/6239142/111321415-480f7900-863e-11eb-83c0-5eb3b8734c4e.jpg)

- `Top Left` - The live feed from the camera. Changes that could trigger a picture will be highlighted by a green rectangle.
- `Top Right` - Camera settings and exposure histogram. Camera settings can be changed with the keys marked `(x)`. The histogram plots the luminance of the image and is used to assist exposure setting.
- `Bottom Left` - The difference between the live and the reference image.
- `Bottom Right` - The difference image clamped to a threshold value, highlighting significant changes.

The camera starts paused: it will take live pictures, but will not take full pictures until unpaused.

A running live picture is taken every 10 seconds. Full-resolution pictures will be taken no quicker than once every 10 seconds. (TODO: Add configuration of this behavior to `config.ini`)

To pause/unpause recording, press `P`.
To exit the app, press `Q`.
