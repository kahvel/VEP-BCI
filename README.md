# VEP-BCI

VEP-BCI implements direct communication channel between the brain and a robot. It translates brain activity into commands for a robot and thus it can be used to control a robot by just looking at certain regions on computer screen without pressing any buttons.

The application was written by Anti Ingel as a practical part of his thesis in University of Tartu.

## Getting started

The application is written in Python 2.7 and can be started by running Main.py in src folder. Currently there is no executable file and to use the application the source code has to be downloaded. See next section for required additional libraries.

## Required additional libraries

The Python version that has been tested is Python 2.7.6 32 bit. Additional libraries that are required along with the version that has been tested are the following:
* pycrypto 2.6
* pywinusb 0.3.3
* numpy 1.8.1
* scipy 0.14.0
* scikit-learn 0.16.1
* psychopy 1.80.06
* wxpython  2.8.12.1
* lxml 3.3.5
* pillow 2.5.0
* pyopengl 3.1.0
* pyglet 1.1.4
* pywin32 219
* PyQT 4.11.3
* pyqtgraph 0.9.10

Code from emokit library was used https://github.com/openyou/emokit/tree/master/python/emokit to access Emotiv EPOC data. 

## Recording brain activity

Inexpensive EEG device Emotiv EPOC is used for recording the brain activity in the application. Other devices can be used too if there is Python script that can access the data in real-time and code in MyEmotiv.py is changed accordingly.
