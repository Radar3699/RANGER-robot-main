#!/usr/bin/env python3

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from pltslamshow import SlamShow

import numpy as np
import cv2
import argparse
import matplotlib.pyplot as plt

# add and parse args
parser = argparse.ArgumentParser()
parser.add_argument("--save", default=False, help='save map True/False')
parser.add_argument("--name", type=str, default='', help='name of map, e.g. map5.jpg')
parser.add_argument("--device", type=str, default='/dev/ttyUSB0', help='connection string for lidar device')
parser.add_argument("--pixelmapsize", type=int, default=500, help='slam map size in pixels')
parser.add_argument("--metermapsize", type=int, default=25, help='slam map size in meters')
parser.add_argument("--minimumsamples", type=int, default=50, help='minimum samples from lidar for scan to be used')
args = parser.parse_args()

# Initialize image dictionary (poplated by vision system) to fuse with slam map
img_dict = {}
img_dict[0] = cv2.flip(cv2.imread('icons8-street-view-50.jpg'),0)
img_dict[1] = cv2.flip(cv2.imread('icons8-staircase-50.jpg'),0)
img_dict[2] = cv2.flip(cv2.imread('icons8-fire-extinguisher-50.jpg'),0)
img_dict[3] = cv2.flip(cv2.imread('icons8-exit-sign-50.jpg'),0)
img_dict[4] = cv2.flip(cv2.imread('icons8-circuit-50.jpg'),0)
img_dict[5] = cv2.flip(cv2.imread('icons8-elevator-50.jpg'),0)
img_dict[6] = cv2.flip(cv2.imread('icons8-test-tube-50.jpg'),0)
img_dict[7] = cv2.flip(cv2.imread('icons8-biohazard-26.jpg'),0)
img_dict[8] = cv2.flip(cv2.imread('icons8-radio-active-50.jpg'),0)
img_dict[9] = cv2.flip(cv2.imread('icons8-door-opened-50.jpg'),0)
temp = np.load('scan.npy')
print(temp)

# Connect to Lidar and initialize variables
lidar = Lidar(args.device)
slam = RMHC_SLAM(LaserModel(), args.pixelmapsize, args.metermapsize)
display = SlamShow(args.pixelmapsize, args.metermapsize*1000/args.pixelmapsize, 'SLAM')
trajectory = []
mapbytes = bytearray(args.pixelmapsize * args.pixelmapsize)
iterator = lidar.iter_scans()
previous_distances = None
previous_angles    = None
next(iterator)
prev_items = None
labels_dict = {}
np.save("label.npy",np.array([]))

### Primary SLAM Loop
while True:

    # Get angles and distance from scan
    try:
        items = [item for item in next(iterator)]
        prev_items = items
    except:
        # If connection drops, reset connection
        print("Exception: ",Exception)
        lidar.stop()
        lidar.disconnect()
        lidar = Lidar(args.device)
        iterator = lidar.iter_scans()
        pass

    distances = [item[2] for item in items]
    angles    = [item[1] for item in items]

    # Incorporate scan by updating SLAM map
    if len(distances) > args.minimumsamples:
        try:
            slam.update(distances, scan_angles_degrees=angles)
        except:
            print("Exception: ",Exception)
            pass
        previous_distances = distances.copy()
        previous_angles    = angles.copy()

    # If cuurent scan not adequate, use previous
    elif previous_distances is not None:
        try:
            slam.update(previous_distances, scan_angles_degrees=previous_angles)
        except:
            print("Exception: ",Exception)
            pass

    # Get current robot position
    try:
        x, y, theta = slam.getpos()
        angle = theta%360

    except:
        print("Exception: ",Exception)
        pass

    # Get current map bytes as grayscale
    try:
        slam.getmap(mapbytes)
    except:
        print("Exception: ",Exception)
        pass

    # Display map
    display.displayMap(mapbytes)

    # Fuse semantic info from Vision system with SLAM map
    if args.save:
        map = np.array(list(mapbytes))
        map = map.reshape((args.pixelmapsize,args.pixelmapsize))
        print("map shape", map.shape)
        map = np.stack((map,)*3,-1)
        square = np.ones((15,15,3))

        # Find wall
        for r in range(0,50000,1):
            xplus=r*np.cos(np.deg2rad(angle))
            yplus=r*np.sin(np.deg2rad(angle))
            xplus = x + xplus
            yplus = y + yplus
            xplus = int(np.floor(xplus/50))
            yplus = int(np.floor(yplus/50))

            if xplus>args.pixelmapsize-11 or xplus<0 or yplus>args.pixelmapsize-11 or yplus<0:
                print("wall outside map bounds")
                break

            # Threshold density for wall
            thresh = 127
            if map[xplus,yplus,0]<thresh:
                print("found wall")

                # Add black square to wall
                map[yplus-7:yplus+8,xplus-7:xplus+8,:] = square

                # Check if label key is on
                arr = np.load('label.npy')
                if len(arr)>0:
                    print("label found: ",arr[0])

                    # If label is r then refresh
                    if arr[0]==99:

                        # Save map
                        for key, value in labels_dict.items():
                            map[key[0]-7:key[0]+8,key[1]-7:key[1]+8,:] = img_dict[value]
                        cv2.imwrite("labelled_" + args.name, cv2.flip(map,0))

                        # Update .npy
                        np.save("label.npy",np.array([]))

                    # If label is num then label
                    else:
                        label = arr[0]
                        image = img_dict[label]

                        # Add to dict of labels
                        labels_dict[(yplus,xplus)] = label

                        # Save map
                        for key, value in labels_dict.items():
                            map[key[0]-7:key[0]+8,key[1]-7:key[1]+8,:] = img_dict[value]
                        cv2.imwrite("labelled_" + args.name, cv2.flip(map,0))

                        # Update .npy
                        np.save("label.npy",np.array([]))

                break
        cv2.imwrite(args.name, cv2.flip(map,0))

    # Display the robot's pose in the map
    display.setPose(x, y, theta)

    # Break on window close
    if not display.refresh():
        break

# Shut down the lidar connection
lidar.stop()
lidar.disconnect()
