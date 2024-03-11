#!/bin/bash

# A script for cutting down bag files

rosbag filter flight1.bag flight1-cut.bag "t.secs >= 1671565228 and t.secs <= 1671566047"
rosbag filter flight2.bag flight2-cut.bag "t.secs >= 1671567362 and t.secs <= 1671568196"
rosbag filter flight3.bag flight3-cut.bag "t.secs >= 1671569339 and t.secs <= 1671570316"
rosbag filter flight4.bag flight4-cut.bag "t.secs >= 1671572257 and t.secs <= 1671573163"


echo "Done!"
