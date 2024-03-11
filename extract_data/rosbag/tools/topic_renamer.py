#!/usr/bin/env python3
import os
import glob

from rosbag import Bag

root_directory = '/media/matt/t7shield/ONR/2021-07-21_Beach/'

bags = sorted(glob.glob(os.path.join(root_directory,"**","*.bag"), recursive=True))

for bagName in bags :
    print("Processing " + bagName)

    inBag = os.path.join(root_directory,bagName)
    outBag_name = os.path.splitext(inBag)[0] + '-mod.bag'

    with Bag(outBag_name, 'w') as outBag:
        for topic, msg, t in Bag(inBag) :
            if topic == '/camera/image_raw' :
                outBag.write('/eo/color/image_raw', msg, t)
            elif topic == '/eo/colour/image_raw/compressed' :
                outBag.write('/eo/color/image_raw/compressed', msg, t)
            elif topic == '/flir_boson/image' :
                outBag.write('/boson/thermal/image_raw', msg, t)
            elif topic == '/flir_cameras/image_raw' :
                outBag.write('/boson/thermal/image_raw', msg, t)
            elif topic == '/flir_cameras/cam_left/image' :
                # Delete this topic, it's useless
                pass
            else:
                outBag.write(topic, msg, t)
