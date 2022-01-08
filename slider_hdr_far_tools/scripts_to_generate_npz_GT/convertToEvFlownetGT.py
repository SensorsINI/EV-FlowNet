#!/usr/bin/env python
import sys
import numpy as np
from rosbag import Bag

def main(argv):
    if len(argv) < 2:
        outputTarget = "evflownet"
    else:
        if argv[1] == "--for-jaer":
            outputTarget = "jaer"
    print('The GT file is generated for: {}'.format(outputTarget))
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
    timeSyn = [a + t_start for a in time]

    # jAER use the first two timestamps to determine the deltaT for the whole file.
    # We manully set it as 100Hz (10ms).
    timeSyn[1] = timeSyn[0] + 0.01
    timeSyn[2] = timeSyn[1] + 0.01

    print(timeSyn[0:10])
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
    jAER treat is a 100Hz(10ms) frame rate.
    But actually it is not.
    The delta time between two frames are not exactly 0.01s.
    To make it more convienient, I intepolate it back as 10ms.
    jAER use the actual size 240x180.
    But on evflownet, I used its default value as MVSEC.
    """
    last_pos = 0
    last_time = 0
    if outputTarget == "jaer":
        dispXArray = np.empty((0, 180, 240), float)
        dispYArray = np.empty((0, 180, 240), float)
    else:
        dispXArray = np.empty((0, 260, 346), float)
        dispYArray = np.empty((0, 260, 346), float)

    for pos, timeTmp in zip(position, time):
        # print('Last position is:{}'.format(last_pos))
        # print('Delta position is:{}'.format(pos - last_pos))
        # print('Delta timestamps is:{}'.format(timeTmp - last_time))
        scaleBackTo10ms = 0.01 / (timeTmp - last_time)
        if outputTarget == "jaer":
            xDisp = (pos - last_pos) / depth * K[0] * scaleBackTo10ms
        else:
            xDisp = -(pos - last_pos) / depth * K[0] * scaleBackTo10ms
        yDisp = 0
        if outputTarget == "jaer":
           dispXArray = np.append(dispXArray, np.full((1, 180, 240), xDisp), axis=0)
           dispYArray = np.append(dispYArray, np.full((1, 180, 240), yDisp), axis=0)
        else:
           dispXArray = np.append(dispXArray, np.full((1, 260, 346), xDisp), axis=0)
           dispYArray = np.append(dispYArray, np.full((1, 260, 346), yDisp), axis=0)
        last_pos = pos
        last_time = timeTmp
        print(xDisp)
        print('Iteration and array shape:{}'.format(dispXArray.shape))


    """
    The evaluation in evflownet required that
    Each gt flow at timestamp gt_timestamps[gt_iter] represents the displacement between
    gt_iter and gt_iter+1.
    """
    if outputTarget == "jaer":
        npzFileName = "slider_hdr_far_gt_flow_jaer.npz"
    else:
        npzFileName = "slider_hdr_far_gt_flow_dist.npz"
    np.savez(npzFileName,
             timestamps=np.stack(timeSyn[0:-1], axis=0),
             x_flow_dist=np.stack(dispXArray[1:, ...], axis=0),
             y_flow_dist=np.stack(dispYArray[1:, ...], axis=0))
    print("Conversion finished.")

if __name__ == "__main__":
    main(sys.argv)
