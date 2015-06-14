# VEP-BCI

VEP-BCI implements direct communication channel between the brain and a robot. It translates brain activity into commands for a robot and thus it can be used to control a robot just by looking at certain regions on a computer screen without pressing any buttons.

<img align="right" src="/docs/images/arrows_chosen.png">

In addition to controlling a robot, the application is a good tool for testing how different parameters affect the performance of the BCI. Currently widely known canonical correlation analysis (CCA) and power spectral density analysis (PSDA) feature extraction methods can be used and their signal pipeline parameters can be easily changed through GUI.

The novelty of the application is that it is able to use multiple feature extraction methods at the same time. Multiple methods complement each other and this approach improves the performance of the BCI.

The application was written by Anti Ingel as a practical part of his thesis in University of Tartu. The thesis Control a Robot via VEP using Emotiv EPOC can be found [here](http://comserv.cs.ut.ee/forms/ati_report/downloader.php?file=FF16189169B7081D7F8121C4E2736D6C8384C450).

## Getting started

The application is written in Python 2.7 and can be started by running Main.py in src folder. Currently there is no executable file and to use the application the source code has to be downloaded. For required libraries see [Required additional libraries](https://github.com/kahvel/VEP-BCI#required-additional-libraries). To actually use the application, brain activity has to be [recorded](https://github.com/kahvel/VEP-BCI#recording-brain-activity). The application is designed to control [PiTank](https://github.com/kahvel/VEP-BCI#the-robot).

## Required additional libraries

The Python version that has been tested is Python 2.7.6 32 bit. Additional libraries that are required along with the version that has been tested are the following:
* pycrypto 2.6
* pywinusb 0.3.3
* numpy 1.8.1
* scipy 0.14.0
* scikit-learn 0.16.1
* psychopy 1.82.01
* wxpython  2.8.12.1
* lxml 3.3.5
* pillow 2.8.1
* pyopengl 3.1.0
* pyglet 1.1.4
* pywin32 219
* PyQT 4.11.3
* pyqtgraph 0.9.10
* OpenCV 2.4.11

Code from emokit library (https://github.com/openyou/emokit/tree/master/python/emokit) was used to access Emotiv EPOC data. 

## The robot

<img align="right" src="/docs/images/robot.png" width="200">

The application can control PiTank (https://github.com/kuz/Garage48-PiTank). The possible commands are move forward, move backward, turn left, turn right and stop. The PiTank has a camera on it and sends the video stream to computer screen.

## Recording brain activity

<img align="right" src="/docs/images/epoc.jpg" width="150">

Inexpensive EEG device Emotiv EPOC is used for recording the brain activity in the application. Emotiv EPOC is portable and easy to use, but since it is so inexpensive, it has lower signal quality than medical-grade devices. Other devices can be used too if there is Python script that can access the data in real-time and code in MyEmotiv.py is changed accordingly.
