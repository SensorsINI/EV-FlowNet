#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from rosbag import Bag
import rosbag

def main():
    inputBag = sys.argv[1]
    outputBag = sys.argv[2]
    print('The input rosbag file is: {}'.format(inputBag))
    print('The output rosbag file is: {}'.format(outputBag))
    with Bag(outputBag, 'w') as output:
        for topic, msg, t in Bag(inputBag):
            if topic == '/dvs/events':
                output.write('/davis/left/events', msg, t)
                output.write('/davis/right/events', msg, t)
            elif topic == '/dvs/image_raw':
                output.write('/davis/left/image_raw', msg, t)
                output.write('/davis/right/image_raw', msg, t)
            else:
                output.write(topic, msg, t)
    print('Conversion finished.')
    # print converted file topics
    bag = rosbag.Bag(outputBag)
    topics = bag.get_type_and_topic_info()[1].keys()
    print(topics)

if __name__ == "__main__":
    main()
