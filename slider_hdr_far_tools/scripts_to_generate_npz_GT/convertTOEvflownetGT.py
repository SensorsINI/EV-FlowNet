#!/usr/bin/env python
import numpy as np
from rosbag import Bag

# Using readlines()
file1 = open('groundtruth.txt', 'r')
Lines = file1.readlines()

time = []
position = []
# Strips the newline character
for line in Lines:
    time.append(line.strip().split()[0])
    position.append(line.strip().split()[1])

time = map(float, time)
position = map(float, position)

"""
Get the start time of the rosbag file so we can syncronize the groundtruth
and the bag file.
"""
bag = Bag("./slider_hdr_far_evflownet.bag")
t_start = bag.get_start_time()
t_end = bag.get_end_time()
print("The bag file start from {:.7f} to {:.7f}.".format(t_start, t_end))
time = [a + t_start for a in time]

# print(time[0:10])
# print(position[0:10])

"""
Input the parameters for the scene and the camera.
Here we use parameters for slider_har_far.
depth is the scene depth, unit is m.
K is the camera parmater matrix, unit is pixel.
The camera parameters are (fx fy cx cy k1 k2 p1 p2 k3)
"""
depth = 0.583
K = [335.419462958, 335.352935612, 129.924663379,
     99.1864303447, -0.138592767408, 0.0933736664192,
     -0.000335586987532, 0.000173720158228, 0.0]

"""
Calculate the displacement in image plane, unit is pixel.
There are only horizontal displacement.
Vertical displacement is zero.
The other thing is that the slider moving direction is opposite
to the OF direction.
"""
last_pos = 0
dispXArray = np.empty((0, 260, 346), float)
dispYArray = np.empty((0, 260, 346), float)
for pos in position:
    xDisp = (pos - last_pos) / depth * K[0]
    yDisp = 0
    dispXArray = np.append(dispXArray, np.full((1, 260, 346), xDisp), axis=0)
    dispYArray = np.append(dispYArray, np.full((1, 260, 346), yDisp), axis=0)
    last_pos = pos
    print(dispXArray.shape)


"""
The evaluation in evflownet required that
Each gt flow at timestamp gt_timestamps[gt_iter] represents the displacement between
gt_iter and gt_iter+1.
"""
np.savez('slider_hdr_far_gt_flow_dist.npz',
         timestamps=np.stack(time[0:-1], axis=0),
         x_flow_dist=np.stack(dispXArray[1:, ...], axis=0),
         y_flow_dist=np.stack(dispYArray[1:, ...], axis=0))
print("Conversion finished.")
