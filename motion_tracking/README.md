We have 12 sequences for SLAM benchmarking. The calibration parameters including the instrinsics and extrinsics betweens sensors can be found in the `configs` folder, which are also the config files to run [VINS_Fusion](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion).  The ground-truth poses are in [TUM format ](https://cvg.cit.tum.de/data/datasets/rgbd-dataset) and saved in the "ground_truth" folder. In the ground-truth poses, the start and end timestamps are there. We also list the start and duration time when playing the rosbag data:

| Bag_Name                                   | bag_sart | bag_durr |
| ------------------------------------------ | -------- | -------- |
| NorthField-2022-07-26-10-39-11             | 0        | -1       |
| NorthField-2022-07-26-10-50-52             | 0        | -1       |
| NorthField-2022-07-26-11-00-21             | 0        | -1       |
| NorthField-2022-07-26-11-05-36             | 0        | -1       |
| NorthField-2022-07-26-11-22-00             | 0        | -1       |
| NorthField-2022-10-06-13-11-26             | 0        | -1       |
| 2022-12-20_CastaicLake/2022-12-20-11-40-28 | 0        | 160      |
| 2022-12-20_CastaicLake/2022-12-20-12-16-02 | 0        | 42       |
| 2022-12-20_CastaicLake/2022-12-20-12-48-59 | 90       | 90       |
| 2022-12-20_CastaicLake/2022-12-20-13-37-37 | 0        | 65       |
| 2023-03-XX_Duck/2023-03-21-14-06-04        | 30       | 30       |
| 2023-03-XX_Duck/2023-03-22-14-31-06        | 40       | 40       |

To play the data with rosbag, run:
```
rosbag play -s $(arg bag_start) -u $(arg bag_durr)  xxx.bag
```




