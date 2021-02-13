import logging
import numpy as np
import skimage as ski
import skimage.util
import skimage.filters
import skimage.color
import skimage.morphology
import skimage.segmentation

logger = logging.getLogger(__name__)


def get_border(img: np.ndarray, thick=10):
    mask = np.zeros_like(img)
    inner_square = img[thick:-thick, thick:-thick]
    mask[thick:-thick, thick:-thick] = np.ones_like(inner_square)
    border = np.ma.array(img, mask=mask)
    return border


def white_border_test(img: np.ndarray, cut=0.95, thick=10):
    img = ski.color.rgb2gray(img)
    border = get_border(img, thick=thick)
    mean = border.mean()
    return mean >= cut


def rgb2rgba(img: np.ndarray):
    alpha = np.full(img.shape[:2], 255, dtype=np.uint8)
    if img.dtype == np.float64:
        alpha = ski.util.img_as_float64(alpha)
    img = np.dstack((img, alpha))
    return img


def erase_masked(img: np.ndarray, mask: np.ndarray):
    img = rgb2rgba(img)
    mask = ski.util.img_as_bool(mask)
    for x, y in np.ndindex(*img.shape[:2]):
        if not mask[x, y]:
            img[x, y][3] = 0
    return img


def luminosity_mask(img: np.ndarray, lum_thresh=0.95, sigma=1, hole_thresh=750):
    img = ski.filters.gaussian(img, sigma=sigma, multichannel=True)
    lum_img = ski.color.rgb2gray(img)
    mask = lum_img < lum_thresh
    mask = ski.morphology.remove_small_holes(mask, area_threshold=hole_thresh)
    return mask


def erase_white_background(img: np.ndarray, lum_thresh=.95, sigma=1, hole_thresh=750, mark_bounds=False):
    mask = luminosity_mask(img, lum_thresh=lum_thresh, sigma=sigma, hole_thresh=hole_thresh)
    if mark_bounds:
        img = ski.segmentation.mark_boundaries(img, ski.util.invert(mask), color=(1, 0, 0))
    else:
        img = erase_masked(img, mask)
    return img
