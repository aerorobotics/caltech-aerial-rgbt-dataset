import argparse
import os

import cv2
import numpy as np
import pandas as pd
from utils.rectifier import StereoRectifier
from utils.autoscale import raw16bit_to_32FC_autoScale
import tqdm

from joblib import Parallel, delayed


def synchronize_df(thermal_sync_csv, mono_sync_csv, color_sync_csv):
    sync_df = pd.read_csv(thermal_sync_csv)
    sync_df.rename(columns={'filename': 'thermal_filepath'}, inplace=True)

    mono_df = pd.read_csv(mono_sync_csv)
    mono_df.rename(columns={'filename': 'mono_filepath'}, inplace=True)
    sync_df = pd.merge_asof(
        sync_df,
        mono_df,
        left_on='Time',
        right_on='Time',
        direction="nearest",
        tolerance=1 / 60
    )

    color_df = pd.read_csv(color_sync_csv)
    color_df.rename(columns={'filename': 'color_filepath'}, inplace=True)
    sync_df = pd.merge_asof(
        sync_df,
        color_df,
        left_on='Time',
        right_on='Time',
        direction="nearest",
        tolerance=1 / 60
    )
    return sync_df


def process_thermal_eo_pair(thermal_img_path, eo_img_path):
    thermal_img = cv2.imread(thermal_img_path, -1)
    eo_img = cv2.imread(eo_img_path, 1)

    H, W, C = eo_img.shape
    tH, tW = thermal_img.shape

    thermal_img_normalized = raw16bit_to_32FC_autoScale(
        thermal_img, [np.percentile(thermal_img, 2), np.percentile(thermal_img, 98)])
    thermal_img_normalized = np.stack([thermal_img_normalized] * 3, axis=2)

    pad_w = int((W - tW) / 2)
    pad_h = int((H - tH) / 2)
    thermal_img = cv2.copyMakeBorder(thermal_img, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, None, 0)
    thermal_img_normalized = cv2.copyMakeBorder(
        thermal_img_normalized, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, None, 0)

    return thermal_img, eo_img, thermal_img_normalized


def stereo_rectify_helper(sr, thermal_img_path, eo_img_path, pair_type, output_dir, rotate180=False):

    assert pair_type in ['thermal_mono', 'thermal_color'], 'pair_type must be either thermal_mono or thermal_color'

    # Create directories
    thermal16_dir = os.path.join(output_dir, pair_type, 'thermal')
    thermal8_dir = os.path.join(output_dir, pair_type, 'thermal8')

    eo_dir = os.path.join(output_dir, pair_type, 'eo')
    sxs_dir = os.path.join(output_dir, pair_type, 'sxs')
    overlay_dir = os.path.join(output_dir, pair_type, 'overlay')

    os.makedirs(thermal16_dir, exist_ok=True)
    os.makedirs(thermal8_dir, exist_ok=True)

    os.makedirs(eo_dir, exist_ok=True)
    os.makedirs(sxs_dir, exist_ok=True)
    os.makedirs(overlay_dir, exist_ok=True)

    # Process image pair
    thermal_img, eo_img, thermal_img_normalized = process_thermal_eo_pair(thermal_img_path, eo_img_path)

    if pair_type == 'thermal_mono':
        thermal_img_rect, _ = sr.rectify_img_pair(thermal_img, eo_img)
        thermal_img_normalized_rect, eo_img_rect = sr.rectify_img_pair(thermal_img_normalized, eo_img)
    elif pair_type == 'thermal_color':
        _, thermal_img_rect = sr.rectify_img_pair(eo_img, thermal_img)
        eo_img_rect, thermal_img_normalized_rect = sr.rectify_img_pair(eo_img, thermal_img_normalized)

    if rotate180:
        eo_img_rect = cv2.rotate(eo_img_rect, cv2.ROTATE_180)
        thermal_img_rect = cv2.rotate(thermal_img_rect, cv2.ROTATE_180)
        thermal_img_normalized_rect = cv2.rotate(thermal_img_normalized_rect, cv2.ROTATE_180)

    thermal_eo_sxs = np.hstack([thermal_img_normalized_rect, eo_img_rect])
    thermal_eo_overlay = cv2.addWeighted(eo_img_rect, 0.4, thermal_img_normalized_rect, 0.5, 0)

    thermal_img_save_path = os.path.join(thermal16_dir, os.path.basename(thermal_img_path))
    thermal8_save_path = os.path.join(thermal8_dir, os.path.basename(thermal_img_path).replace('.tiff', '.png'))
    eo_save_path = os.path.join(eo_dir, os.path.basename(
        thermal_img_path).replace('.tiff', '.png').replace('thermal', 'eo'))
    sxs_save_path = os.path.join(sxs_dir, os.path.basename(
        thermal_img_path).replace('.tiff', '.png').replace('thermal', 'sxs'))
    overlay_save_path = os.path.join(overlay_dir, os.path.basename(
        thermal_img_path).replace('.tiff', '.png').replace('thermal', 'overlay'))

    cv2.imwrite(thermal_img_save_path, thermal_img_rect)
    cv2.imwrite(thermal8_save_path, thermal_img_normalized_rect)
    cv2.imwrite(eo_save_path, eo_img_rect)
    cv2.imwrite(sxs_save_path, thermal_eo_sxs)
    cv2.imwrite(overlay_save_path, thermal_eo_overlay)


def stereo_rectify_df(data_dir, sync_df, thermal_mono_10x10_calib_yaml, color_thermal_10x10_calib_yaml, output_dir, rotate180=False):
    sr_thermal_mono = StereoRectifier(thermal_mono_10x10_calib_yaml)
    sr_color_thermal = StereoRectifier(color_thermal_10x10_calib_yaml)

    for idx, row in tqdm.tqdm(sync_df.iterrows(), total=len(sync_df)):
        thermal_img_path = os.path.join(data_dir, row['thermal_filepath'])

        # Do a null check on the filepaths
        if type(row['mono_filepath']) == str:
            mono_img_path = os.path.join(data_dir, row['mono_filepath'])
            stereo_rectify_helper(sr_thermal_mono, thermal_img_path, mono_img_path,
                                  'thermal_mono', output_dir, rotate180)
        if type(row['color_filepath']) == str:
            color_img_path = os.path.join(data_dir, row['color_filepath'])
            stereo_rectify_helper(sr_color_thermal, thermal_img_path, color_img_path,
                                  'thermal_color', output_dir, rotate180)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, required=True, help='Must contain data_dir/csv/*.csv')
    parser.add_argument('--thermal_csv', type=str, required=True)
    parser.add_argument('--mono_csv', type=str, required=True)
    parser.add_argument('--color_csv', type=str, required=True)
    parser.add_argument('--rotate180', action='store_true')

    parser.add_argument('--thermal_mono_calib_yaml', type=str,
                        default='calibrations/thermal_mono_10x10_calib.yaml')
    parser.add_argument('--color_thermal_calib_yaml', type=str,
                        default='calibrations/color_thermal_10x10_calib.yaml')

    parser.add_argument('--output_dir', type=str, required=True)
    args = parser.parse_args()
    print(args)

    csv_dir = os.path.join(args.data_dir, 'csv')

    thermal_sync_csv = os.path.join(csv_dir, args.thermal_csv)
    mono_sync_csv = os.path.join(csv_dir, args.mono_csv)
    color_sync_csv = os.path.join(csv_dir, args.color_csv)

    sync_df = synchronize_df(thermal_sync_csv, mono_sync_csv, color_sync_csv)
    # stereo_rectify_df(args.data_dir, sync_df, args.thermal_mono_calib_yaml,
    #                   args.color_thermal_calib_yaml, args.output_dir, rotate180=args.rotate180)

    n_jobs = 8
    results = Parallel(n_jobs=n_jobs)(delayed(stereo_rectify_df)(
        args.data_dir,
        df,
        args.thermal_mono_calib_yaml,
        args.color_thermal_calib_yaml,
        args.output_dir,
        rotate180=args.rotate180
    )
        for df in np.array_split(sync_df, n_jobs)
    )
