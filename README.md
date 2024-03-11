# Caltech Aerial RGB-Thermal Dataset

![teaser](https://github.com/aerorobotics/caltech-aerial-rgbt-dataset/assets/6981697/c6b7dc3c-3858-499b-ae17-90da426694ea) 

Welcome to the Caltech Aerial RGB-Thermal dataset repository! This repository hosts the first publicly available dataset tailored for aerial robotics operating in diverse natural landscapes across the continental United States. Our dataset comprises synchronized RGB, thermal, GPS, and IMU data, providing a comprehensive resource for researchers and practitioners in the field. For further details, please see our paper: 

PAPER_TITLE



**Key Features:**

- 🏞️ **Diverse Terrains**: Our dataset captures a wide range of terrains, including rivers, lakes, coastlines, deserts, and forests, ensuring robustness to various environmental conditions.

- 🖼️ **Semantic Segmentation Annotations**: We provide semantic segmentation annotations for 10 classes commonly encountered in natural settings, facilitating the development of perception algorithms resilient to adverse weather and nighttime conditions.

- 📊 **Benchmarking**: We introduce new benchmarks for thermal and RGB-T semantic segmentation, RGB-T image translation, and visual-inertial odometry, presenting challenging tasks for evaluation and comparison.

- 🌟 **Challenging Domain Shifts**: We provide splits for the data based on time and geography, enabling studies of geographic domain adaptation. Temporal splits enable new studies into better handling thermal inversion (see image below). 


## Dataset Capture Locations
<p align="center">
  <img src="https://github.com/aerorobotics/caltech-aerial-rgbt-dataset/assets/6981697/1050a823-aca9-4e45-85fd-609f3aa18d35" width="100%">
</p>

## Thermal Inversion Example
<p align="center">
  <img src="https://github.com/aerorobotics/caltech-aerial-rgbt-dataset/assets/6981697/11d65042-40d4-4d1d-9bb2-e430617a708c" width="100%">
</p>

## Dataset Download
Coming soon!

### Dataset Organization
- Raw data is located at `onr-processed`
- Annotated thermal data is located here under `labeled_thermal_singles`. Images are stored according to their capture location and trajectory id following the pattern:
```
labeled_thermal_singles/CAPTURE_PLACE/TRAJECTORY_ID/{masks|thermal8|thermal16}
```
- Annotated paired RGB-T data is located under `labeled_rgbt_pairs`. 


## Semantic Segmentation & Image Translation

### Semantic Segmentation Classes
| Index |Class | Hex Code | Color |
| --- | --- | --- | --- |
| 0 | unknown | #FF2400 | <span align="center"><img src="examples/class_colors/Unknown.png" width=30px height=30px/></span> |
| 1 | background | #000000 | <span align="center"><img src="examples/class_colors/__background__.png" width=30px height=30px/></span> |
| 2 | bare ground | #F2D8C4 | <span align="center"><img src="examples/class_colors/Bare_ground.png" width=30px height=30px/></span> |
| 3 | boulders / rocky terrain | #594636 | <span align="center"><img src="examples/class_colors/Boulders___rocky_terrain.png" width=30px height=30px/></span> |
| 4 | human-made structures | #A6A6A6 | <span align="center"><img src="examples/class_colors/Human-made_structures.png" width=30px height=30px/></span> |
| 5 | road | #52595A | <span align="center"><img src="examples/class_colors/Road.png" width=30px height=30px/></span> |
| 6 | shrubs | #9BE600 | <span align="center"><img src="examples/class_colors/Shrubs.png" width=30px height=30px/></span> |
| 7 | trees | #008A35 | <span align="center"><img src="examples/class_colors/Trees.png" width=30px height=30px/></span> |
| 8 | sky | #00D8F5 | <span align="center"><img src="examples/class_colors/Sky.png" width=30px height=30px/></span> |
| 9 | water | #0D7FFC | <span align="center"><img src="examples/class_colors/Water.png" width=30px height=30px/></span> |
| 10 | vehicles | #FFF900 | <span align="center"><img src="examples/class_colors/Vehicles.png" width=30px height=30px/></span> |
| 11 | person | #FE00AA | <span align="center"><img src="examples/class_colors/Person.png" width=30px height=30px/></span> |

We typically ignore `unknown` and `background` classes.

### Dataset Splits
Thermal data splits are located under `caltech_aerial_thermal_dataset/splits/thermal_splits` and are subdivided into general (random), geographic (state-based and terrain-based), and temporal (sunrise vs. day vs. night) splits. 

The split for RGB-T paired imagery is created from the general (random) split and is available under `caltech_aerial_thermal_dataset/splits/rgbt_splits`. There are less samples in this split due to sensor failures during some flights.



## Data Processing

### Dataset Summary
COMING SOON!

### Data Extraction
#### ROS Bagfile
The dataset is provided primarily as ROS1 rosbags. As rosbags may not be a convenient filetype for all users, extraction scripts have been provided to extract csv and jpg/png files.  Please see the readme at `/extract_data/rosbag/README.md` for more information.

#### Ardupilot
Where available, the raw onboard logs from Ardupilot have been included in the dataset.  As not all users will be able to read these directly, extraction scripts have been included as part of this repository.  Please see the readme at `/extract_data/ardupilot/README.md` for more information.

### Data Streams
#### Preferred Position Data
COMING SOON!

#### Synchronization Data
COMING SOON!

### Rectification
All images with semantic segmentation annotations are already rectified. If you want to rectify all images, some code is provided to assist you in this:

To rectify raw imagery, use the `MonoRectifier` class provided in `caltech_aerial_thermal_dataset/utils/rectifier.py`. Use the appropriate calibration files provided under `calibrations/*.yaml`.

To stereo rectify a trajectory, follow the example bash scripts here:
```
caltech_aerial_thermal_dataset/bash/bulk_stereo_rectify.sh
caltech_aerial_thermal_dataset/bash/stereo_rectify.sh
```
and check out the command-line arguments listed in `stereo_rectify.py`

## Issues and Contributing
If you find issues with this repo, or have code to contribute, please submit and issue and/or a PR above.

## License