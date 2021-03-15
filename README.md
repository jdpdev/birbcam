# birbcam

A Raspberry Pi-powered, motion-activated camera for watching bird feeders.

## Set Up
### Environment

Tested with Python 3.7.3 on a Raspberry Pi 4 Model B (4GB RAM) running Raspbian Buster, using the Camera Module V2 and HQ cameras.

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

- `Top Left` - The live feed from the camera. Changes that could trigger a picture will be highlighted by a green rectangle.
- `Top Right` - Camera settings and exposure histogram. Camera settings can be changed with the keys marked `(x)`. The histogram plots the luminance of the image and is used to assist exposure setting.
- `Bottom Left` - The current average image being used to detect changes.
- `Bottom Right` - The difference between the live and average images, used to determine if changes are significant enough to take a picture.

The camera starts paused: it will take live pictures, but will not take full pictures until unpaused.

A running live picture is taken every 10 seconds. Full-resolution pictures will be taken no quicker than once every 10 seconds. (TODO: Add configuration of this behavior to `config.ini`)

To pause/unpause recording, press `P`.
To exit the app, press `Q`.
