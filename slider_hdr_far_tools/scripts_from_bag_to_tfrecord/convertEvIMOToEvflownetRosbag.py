#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
This file is used to convert EV-IMO rosbag to a standard that is
supported by evflownet and thus it could be further coverted to
tfrecord further.
Ev-imo dataset uses Samsung VGA DVS camera.
The APS images are from another different camera and stored in a compressed
msg format. To use it on Ev-flownet, we need to decompress it back to raw data.
"""
import sys
from rosbag import Bag
import rosbag
import cv2
from cv_bridge import CvBridge

br = CvBridge()

def main():
    inputBag = sys.argv[1]
    outputBag = sys.argv[2]
    print('The input rosbag file is: {}'.format(inputBag))
    print('The output rosbag file is: {}'.format(outputBag))
    with Bag(outputBag, 'w') as output:
        count = 0
        for topic, msg, t in Bag('/media/minliu/dataset/google_download/scene9_dyn_train_06.bag'):
            if topic == '/samsung/camera/events':
                 output.write('/davis/left/events', msg, t)
                 # output.write('/davis/right/events', msg, t)
            elif topic == '/flea3/image_color/compressed':
                 im = br.compressed_imgmsg_to_cv2(msg)
                 im_resized = cv2.resize(im, (640, 480))
                 im_gray = cv2.cvtColor(im_resized, cv2.COLOR_BGR2GRAY)
                 filename = 'output/image_{}.png'.format(count)
                 # cv2.imwrite(filename, im_resized)
                 raw_msg = br.cv2_to_imgmsg(im_gray)
                 raw_msg.header.stamp = t
                 output.write('/davis/left/image_raw', raw_msg, t)
                 # output.write('/davis/right/image_raw', raw_msg, t)
                 # print('time stamp is {}.'.format(t))
                 count += 1
                 if count%10 == 0:
                    print('Finished {} image msgs.'.format(count))
            # else:
                # output.write(topic, msg, t)
    print('Conversion finished.')
    # print converted file topics
    bag = rosbag.Bag(outputBag)
    topics = bag.get_type_and_topic_info()[1].keys()
    print(topics)

if __name__ == "__main__":
    main()
