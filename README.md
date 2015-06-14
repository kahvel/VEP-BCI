# VEP-BCI

VEP-BCI implements direct communication channel between the brain and a robot. It translates brain activity into commands for a robot and thus it can be used to control a robot just by looking at certain regions on a computer screen without pressing any buttons.

<img align="right" src="/docs/images/arrows_chosen.png" width="300">

In addition to controlling a robot, the application is a good tool for testing how different parameters affect the performance of the BCI. Currently widely known canonical correlation analysis (CCA) and power spectral density analysis (PSDA) feature extraction methods can be used and their signal pipeline parameters can be easily changed through GUI.

The novelty of the application is that it is able to use multiple feature extraction methods at the same time. Multiple methods complement each other and this approach improves the performance of the BCI.

The application was written by Anti Ingel (antiingel@gmail.com) as a practical part of his thesis in University of Tartu. The thesis Control a Robot via VEP using Emotiv EPOC can be found [here](http://comserv.cs.ut.ee/forms/ati_report/downloader.php?file=FF16189169B7081D7F8121C4E2736D6C8384C450).

For a very brief overview of the thesis see this [poster](https://github.com/kahvel/VEP-BCI/blob/master/docs/images/poster.pdf).

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
<br>
<br>
## Usage instructions
### Window tab

<img align="right" src="/docs/images/window.png" width="300">

In this tab options of the window that is presenting visual stimuli can be changed. Options are the following:
* Width - the width of the window in pixels.
* Height - the height of the window in pixels.
* Color - the background color of the window.
* Freq - refresh rate of the monitor used for displaying visual stimuli. There is no need to change it manually - by clicking Refresh the application automatically updates the Freq field and all the target frequencies accordingly.
* Monitor - menu for choosing monitor that is used for displaying visual stimuli. That is used only to automatically detect refresh rate if multiple monitors are connected to the computer.
* Disable - disable the window. If disabled, the application starts without the window for displaying visual stimuli.

### Targets tab

<img align="right" src="/docs/images/targets.png" width="300">

In this tab options of the visual stimuli or targets can be changed. Options are the following:
* Freq - the blinking frequency of the target. Can be increased and decreased by clicking + and - buttons. When updating this field, Sequence updates automatically.
* Harmonics - the harmonics used in feature extraction separated by commas.
* Sequence - the blinking or flickering sequence consisting of ones and zeros. Targets have two possible states. One represents one of them and zero the other. When updating this field, Freq updates automatically.
* Width - the width of the target in pixels.
* Height - the height of the target in pixels.
* x - the x coordinate of the centre of the target in pixels. (0, 0) is in the middle of the screen.
* y - the y coordinate of the centre of the target in pixels. (0, 0) is in the middle of the screen.
* Color1 - the color of the target in the state represented by one.
* Color2 - the color of the target in the state represented by zero.
* Disable - disable current target. If disabled, this target is not displayed on the window that displays targets.
* Delete - delete current target.

### Extraction tab

<img align="right" src="/docs/images/extraction.png" width="300">

In this tab options of the feature extraction methods can be changed. For more information see the [thesis](http://comserv.cs.ut.ee/forms/ati_report/downloader.php?file=FF16189169B7081D7F8121C4E2736D6C8384C450). Options are the following:
* Emotiv EPOC channels that are used in feature extraction methods can be chosen with checkboxes. 
* Feature extraction methods can be chosen with buttons PSDA, sum PSDA, CCA.
* Detrend - menu for choosing detrending settings. See [SciPy documentation](http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.detrend.html) for more details.
* Window - menu for choosing a window function. See [SciPy documentation](http://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.signal.get_window.html) for more details.
* Interp - menu for choosing interpolation settings. Interpolation is used only with PSDA and sum PSDA methods. See [SciPy documentation](http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.interp1d.html) for more details.
* Filter - menu for choosing filtering settings. See [SciPy documentation](http://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.signal.firwin.html#scipy.signal.firwin) for more details.
* Length - the length of the window in packets. For example, Emotiv EPOC has sampling frequency of 128 Hz and thus 128 packets = 1 second.
* Step - step between feature extractions or the amount of packets that has to be received before each feature extraction.
* Break - the number of breakpoints in detrending. See [SciPy documentation](http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.detrend.html) for more details.
* Arg - Kaiser window beta argument. See [NumPy documentation](http://docs.scipy.org/doc/numpy/reference/generated/numpy.kaiser.html) for more details.
* From, To and Taps - filter arguments. See [SciPy documentation](http://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.signal.firwin.html#scipy.signal.firwin) for more details.
* Normalise - whether to normalise power spectral density or not.
* Disable - disable current feature extraction methods.

### Plot tab

<img align="right" src="/docs/images/plot.png" width="300">

In this tab options of real-time plotting can be changed. Most options are the same as in Extraction tab. Options different than in extraction tab:
* Plot type:
 * Signal - plot the signal separately for each channel.
 * Sum signal - add all the signals up and plot the result.
 * Avg signal - plot the average signal for each channel.
 * Sum avg signal - add all the average signals up and plot the result.
 * Power - plot the power spectral density for each channel.
 * Sum power - add all the signals up and plot the result's power spectral density
 * Avg power - plot the average signal's power spectral density for each channel.
 * Sum avg power - add all the average signals up and plot the result's power spectral density.

### Test tab

<img align="right" src="/docs/images/test.png" width="300">

In this tab options for testing the application can be chosen. Options are the following:
* Test target - the target that is being tested, so that the application knows which target the user is looking at to calculate accuracy etc. The number corresponds to target's number in target tab. Random means that application generates random testing sequence.
* Standby - one target can be chosen as standby target. After choosing standby target, the application goes to switches between normal and standby mode.
* Time - the amount of time in packets to test the application. After the amount of time has passed, application automatically stops. 
* Unlimited - if no time limit is required then this checkbox should be chosen. Then the application does not stop automatically.
* Results
 * Show - print the results to console.
 * Reset - reset results. Results of consequtive trials can be seen separately even without resetting the results.
 * Save - save the results to a file.

### Robot tab

<img align="right" src="/docs/images/robot_gui.png" width="300">

In this tab robot options can be changed. Options are the following:
* Forward, Backward, Left, Right and Stop - for each command a corresponding target can be chosen. The number corresponds to target's number in target tab. Each command can be tested by cliking Test button.
* x - the x coordinate of the camera stream on the targets window. (0, 0) is in the middle of the screen.
* y - the y coordinate of the camera stream on the targets window. (0, 0) is in the middle of the screen.
* Width - the width of the camera stream.
* Height - the height of the camera stream.
* Stream - whether to show the stream or not.
* Disable - disable the robot.
