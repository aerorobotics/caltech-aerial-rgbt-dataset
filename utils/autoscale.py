import numpy as np
from skimage import exposure


def raw16bit_to_32FC_autoScale(img, equalize_hist=True):
    img = img - np.percentile(img, 1)
    img = img / np.percentile(img, 99)
    img = np.clip(img, 0, 1)

    if equalize_hist:
        img = exposure.equalize_adapthist(img, clip_limit=0.01)

    return 255 * img
