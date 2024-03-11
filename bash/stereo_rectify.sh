PLACE=$1
THERMAL_CSV=$2
COLOR_CSV=$3
MONO_CSV=$4

DATA_PATH=onr-thermal
OUTPUT_DIR=onr-thermal-paired
for TRAJECTORY_PATH in ${DATA_PATH}/${PLACE}/*/csv ; do
    TRAJECTORY=$(basename $(dirname $TRAJECTORY_PATH))

    python stereo_rectify.py \
    --data_dir ${DATA_PATH}/${PLACE}/${TRAJECTORY} \
    --thermal_csv ${THERMAL_CSV}.csv \
    --color_csv ${COLOR_CSV}.csv \
    --mono_csv ${MONO_CSV}.csv \
    --output_dir ${OUTPUT_DIR}/${PLACE}/${TRAJECTORY}/stereo_rectified
    # --rotate180
done