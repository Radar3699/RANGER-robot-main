# RANGER Robot

This repo details some of the key backend pieces I implimented for the RANGER (Robotic Artificially intelligent Navigator for General Emergency Response), which hopefully can be of use elsewhere.

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/P1.png)

## Deep Vision and SLAM

RANGER's Vision and SLAM backends leverage GPU processing and deep learning for intelligent environment analysis and navigation. 

### Hardware Pipeline

The current setup is built for the following hardware pipeline: 

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/P2.png)

A key benefit of the RANGER system is the expensive computing hardware is not in danger. Thus we use a suite of microcomputers serving as middle men to stream raw sensory data over a web server to and from a GPU groundstation (either desktop hardware with a GPU or cloud server with GPU capability). 

### Sensory Input / Output Pipeline

The groundstation then leverages a set of machine learning and deep learning algorithms to process the raw sensory input into a bird's eye map of the robots environment with objects of interest labelled. This processing follows the following schema:

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/P3.png)

In manual control mode the map is saved for various environments and serves as a compact representation of the robot's environment. In Autonomous mode Djiksta's algorithm can be run on this map, where adjecent pixels are plugged in as a k-regular graph with distance 1 between them for intensity less than 50, and object pixels are plugged in with distance 10. The end point can either be a pre-set destination or a home point for return to home functionality. 

### Deep Vision System

The vision (object detection and localization) component leverages a 106 layer YOLO-V3 (You Only Look Once) deep learning architecture trained from scratch on an augmented MSCOCO dataset. The training took 3 days on an NVidia GPU. Below are two examples of the network running in non-streaming mode on movie clips.

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V3.gif)

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V4.gif)

The following are two examples of the network running on streaming live camera data where we are able to achieve a stable 15-25 frames per second by running on the GPU and by multi-threading the incoming camera streams, web server, and deep network feedforwarding. The second clip highlights some of the augmented custom classes 

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V1.gif)

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V2.gif)

### SLAM (Simultanious Localization and Mapping)

RANGER impliments a BreezySLAM system for fusing LiDAR (Light Detection and Ranging) scans into a map, then fuses semantic information from the cameras into labels for the map. Below are some examples of the SLAM system running:

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V5.gif)

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V6.gif)

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V7.gif)

![alt text](https://github.com/Radar3699/RANGER/blob/master/Demos/V8.gif)

Semantic info is communicated to the primary SLAM loop by populating `labels.npy` with a class identifier. Normally this is populated by the primary Vision loop but a manual populating loop script is also included which is useful for debugging.

## Control Scripts

RANGER's control scripts were designed from the ground up as a serial-level high latency tolerant system suitable for manual (WASD) control through secure shell as well as autonomous (X,Y relative to robot center) control. The current implimentation is designed for a DHB-10 motor controller but can be easily changed for other systems because system specific communication functions are abstracted away in `ArloUtils.py`.

### WASD Control

For Manual control invoking `WASDControl.py` is recommended. The following brings up the control center HUD, and is typically invoked by first SSHing into the robot's central control microcomputer (UDOO in this case, which sends serial commands to an arduino which then sends to the DHB10 motor controller). 

```
python WASDControl.py --connect '/dev/ttyACM0' --speed 800 --flip False
```

Seeing an `A` or other read string printed in the console before the HUD comes up indicates a good readable connection. 

Connect is the connection string used by pyserial to establish a serial connection, speed is the speed in motor counts/second, and flip is whether or not to frip the robots direction of travel and useful is the robot doesn't have a specific front and back. The defaults are shown above, for more info type

```
python WASDControl.py --help
``` 

The user is presented with a curses window displaying the current direction of travel, slider for turning left and right in 10 degree eincriments, and current speed setting. The speed setting can be adjusted by pressing `-` to decriment the speed by 100 counts/second and `=` to incriment the speed by 100 counts/second. From stationary, `w` sends a 'go' command to the robot invoking forward motion until `s` is pressed. For crawling the number keys are used. `1` sends a move forward 10 cm command, `2` sends a move 20 cm command, ... , and `9` sends a move 90 cm command. From stationary `s` sends a turn 180 degree command, `a` sends as 90 degree left turn command, and `d` sends a 90 degree turn right command. More precise turning is achieved by tapping or holding `q` and `e` to "charge" the turn slider left or right in 10 degree incriments, pressing `space` then "releases" the turn slider sending a turn command with the specific degrees to the robot. 

The following command system was converged to after multiple iterations of testing and was designed to work well with high latency systems, over secure shell, and across various control platforms (Linux, Mac, PC) without system-propietary packages. The above commands don't need to be memorized as they are layed our pictorially via ascii art in the main control HUD.

### X,Y Control

The robot can also be driven by sending X,Y coordinates in meters relative to the middle of the robot. This is generally significantly less intuitive than WASD control but can be useful for debugging purposes. It's primary purpose is for autonomous control by converting a path obtained from Djiksta's algorithm to a sequence of actionable commands. 

```
python ManualXYControl.py --connect '/dev/ttyACM0' --speed 800 --flip False
```

Where the command line argument definitions are the same as for WASD. Running the above will bring up a recurring prompt for X Y position which are input as two ints or floats E.g. 

```
(x,y):
```
Should be responded to by typing 

```
-1.5 1.0
```

If the new desired position is 1.5 meters South and 1 meter East. The robot will always turn before moving so it will always be facing the direction it's moving. The 'front' of the robot can be flipped by setting the CLA `Flip` to `True`.

### Control Testing (Robot Waltz)

The easiest way to test if a communication interface is implimented correctly in `ArloUtils.py` is to run 

```
python ArloTestDance.py --connect '/dev/ttyACM0' --speed 800 --flip False
```

Which will make the robot do a Waltz Box (or a robot's best approximation of one).  This tests a suite of go, stop, crawl, and turn commands both forwards and backwards and is considered successful if the robot finishes the dance in its original orientation.

## Built with

* [YOLO](https://pjreddie.com/darknet/yolo/) - The architecture used for vision training
* [DarkFlow](https://github.com/thtrieu/darkflow) - The framework used to convert darknet YOLO to tensorflow
* [Tensorflow-gpu](https://www.tensorflow.org/) - The framework used for network inference
* [CUDA](https://developer.nvidia.com/cuda-zone) - Paralell GPU computing platform for NVidia GPUs used in combination with TensorFlow
* [BreezySLAM](https://github.com/simondlevy/BreezySLAM) - SLAM algorithm used
* [Devicehive](https://devicehive.com/) - The web server platform used for streaming video data over HTTP and RTSP
* [OpenCV](https://opencv.org/) - The framework used for interfacing with camera hardware
* [Python Curses](https://docs.python.org/3/howto/curses.html) - The python package used ot built the HUD for manual WASD control
* [Python Numpy](http://www.numpy.org/) - Numerical computing library used

