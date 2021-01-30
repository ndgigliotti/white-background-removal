import logging
import numpy as np
import skimage as ski

logger = logging.getLogger(__name__)


def denormalize(img: np.ndarray):
    return ski.util.img_as_ubyte(img)


def normalize(img: np.ndarray):
    return ski.util.img_as_float64(img)


def rgb2rgba(img: np.ndarray):
    alpha = np.full(img.shape[:2], 255, dtype=np.uint8)
    if img.dtype == np.float64:
        alpha = normalize(alpha)
    img = np.dstack((img, alpha))
    return img


def erase_masked(img: np.ndarray, mask: np.ndarray):
    img = rgb2rgba(img)
    mask = ski.util.img_as_bool(mask)
    for x, y in np.ndindex(*img.shape[:2]):
        if not mask[x, y]:
            img[x, y][3] = 0
    return img


def luminosity_mask(img: np.ndarray, thresh=0.95, sigma=1, min_hole_size=750):
    img = ski.filters.gaussian(img, sigma=sigma, multichannel=True)
    lum = ski.color.rgb2gray(img)
    mask = lum < thresh
    mask = ski.morphology.remove_small_holes(mask, area_threshold=min_hole_size)
    return mask


def erase_white_background(img: np.ndarray, thresh=.95, sigma=1, min_hole_size=750, mark_bounds=False):
    mask = luminosity_mask(img, thresh=thresh, sigma=sigma, min_hole_size=min_hole_size)
    if mark_bounds:
        img = ski.segmentation.mark_boundaries(img, ski.util.invert(mask), color=(1, 0, 0))
    else:
        img = erase_masked(img, mask)
    return img
