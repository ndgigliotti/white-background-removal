import logging
import numpy as np
import skimage as ski
import skimage.util
import skimage.filters
import skimage.color
import skimage.morphology
import skimage.segmentation

logger = logging.getLogger(__name__)


def get_border(image: np.ndarray, thick=10):
    mask = np.zeros_like(image)
    inner_square = image[thick:-thick, thick:-thick]
    mask[thick:-thick, thick:-thick] = np.ones_like(inner_square)
    border = np.ma.array(image, mask=mask)
    return border


def get_sides(image: np.ndarray, thick=10):
    top = image[:thick]
    right = image[:, -thick:]
    bottom = image[-thick:]
    left = image[:, :thick]
    return top, right, bottom, left


def white_border_test(image: np.ndarray, lum_thresh=0.95, thick=10, n_sides=3, metric=np.mean):
    image = ski.color.rgb2gray(image)
    sides = get_sides(image, thick=thick)
    values = np.array([metric(x) for x in sides])
    n_pass = np.count_nonzero(values >= lum_thresh)
    return n_pass >= n_sides


def white_border_test2(image: np.ndarray, lum_thresh=0.95, thick=10, metric=np.mean):
    image = ski.color.rgb2gray(image)
    border = get_border(image, thick=thick)
    value = metric(border)
    return value >= lum_thresh


def rgb2rgba(image: np.ndarray):
    alpha = np.full(image.shape[:2], 255, dtype=np.uint8)
    if image.dtype == np.float64:
        alpha = ski.util.img_as_float64(alpha)
    image = np.dstack((image, alpha))
    return image


def erase_masked(image: np.ndarray, mask: np.ndarray):
    mask = np.dstack([mask]*4)
    ma_image = np.ma.array(rgb2rgba(image), mask=mask)
    return ma_image.filled(fill_value=[0]*4)


def luminosity_mask(image: np.ndarray, lum_thresh=0.95, sigma=1, hole_thresh=750, masked_value=True):
    image = ski.filters.gaussian(image, sigma=sigma, multichannel=True)
    lum_image = ski.color.rgb2gray(image)
    mask = lum_image >= lum_thresh
    mask = ski.morphology.remove_small_objects(mask, min_size=hole_thresh)
    if not masked_value:
        mask = np.logical_not(mask)
    return mask


def erase_white_background(image: np.ndarray, lum_thresh=0.95, sigma=1, hole_thresh=750, mark_bounds=False):
    mask = luminosity_mask(image, lum_thresh, sigma, hole_thresh, True)
    if mark_bounds:
        image = ski.segmentation.mark_boundaries(image, mask, color=(1, 0, 0))
    else:
        image = erase_masked(image, mask)
    return image
