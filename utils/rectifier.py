import numpy as np
import cv2
import yaml


class MonoRectifier:

    # ROS calibration files
    def __init__(self, yaml_file):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            self.W, self.H = data['image_width'], data['image_height']

            self.D = np.array(data['distortion_coefficients']['data'])
            self.I = np.array(data['camera_matrix']['data']).reshape(3, 3)
            self.P = np.array(data['projection_matrix']['data']).reshape(3, 4)

            print('Distortion coefficients: ', self.D)
        self.newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.I, self.D, (self.W, self.H), 0, (self.W, self.H))
        self.new_P = np.hstack([self.newcameramtx, np.zeros((3, 1))])

    def rectify(self, raw_img, rotate_180=False):
        img = cv2.undistort(raw_img, self.I, self.D, None, self.newcameramtx)
        if rotate_180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        return img


class StereoRectifier:

    # Kalibr calibration files
    def __init__(self, yaml_file):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            self.W0, self.H0 = data["cam0"]["resolution"]
            self.W1, self.H1 = data["cam1"]["resolution"]

            cam0_data, cam1_data, self.Q, self.roi_0, self.roi_1 = self.convert(data)
            self.K0, self.D0, self.R0, self.P0 = cam0_data
            self.K1, self.D1, self.R1, self.P1 = cam1_data

    def load_matrices(self, data):
        intrinsics = data["intrinsics"]

        K = np.eye(3)
        np.fill_diagonal(K[:2, :2], intrinsics[:2])
        K[:2, 2] = intrinsics[2:]

        D = np.zeros(5)
        D[:4] = data["distortion_coeffs"]
        return K, D

    def convert(self, data):
        K0, D0 = self.load_matrices(data["cam0"])
        K1, D1 = self.load_matrices(data["cam1"])
        # T_01 = np.linalg.inv(np.array(data["cam1"]["T_cn_cnm1"]))
        T_01 = np.array(data["cam1"]["T_cn_cnm1"])
        self.T_01 = T_01
        R = T_01[:3, :3]
        T = T_01[:3, 3]
        self.R = R
        self.T = T
        Size = tuple(data["cam0"]["resolution"])  # Assumes both cameras have same resolution

        R0, R1, P0, P1, Q, roi_0, roi_1 = cv2.stereoRectify(
            cameraMatrix1=K0, cameraMatrix2=K1,
            distCoeffs1=D0, distCoeffs2=D1, imageSize=Size, R=R, T=T, flags=cv2.CALIB_ZERO_DISPARITY, alpha=0)
        return (K0, D0, R0, P0), (K1, D1, R1, P1), Q, roi_0, roi_1

    def rectify_img_pair(self, img0, img1):

        xmap0, ymap0 = cv2.initUndistortRectifyMap(self.K0, self.D0, self.R0, self.P0, (self.W0, self.H0), cv2.CV_32FC1)
        xmap1, ymap1 = cv2.initUndistortRectifyMap(self.K1, self.D1, self.R1, self.P1, (self.W1, self.H1), cv2.CV_32FC1)
        img0 = cv2.remap(img0, xmap0, ymap0, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
        img1 = cv2.remap(img1, xmap1, ymap1, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)

        return img0, img1
