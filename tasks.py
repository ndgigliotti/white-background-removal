import os
import logging
import time
from pprint import pformat
import skimage as ski
import skimage.io
import core
import util

logger = logging.getLogger(__name__)


def _log_strings(strings: list, level=logging.INFO):
    """Pretty print a list of strings to the log."""
    strings = pformat(strings).split("\n")
    for string in strings:
        logger.log(level, string)


def load_images(pool, entries):
    """Load images from paths in `entries`."""
    start = time.perf_counter()
    images = pool.map(ski.io.imread, [x.path for x in entries])
    logger.info("Loaded %i images:", len(images))
    _log_strings([x.name for x in entries])
    logger.info(util.elapsed(start))
    logger.info("\n")
    return images


def check_border(pool, images, entries):
    """Run the white border test, then remove images that fail (in place)."""
    start = time.perf_counter()
    test_results = pool.map(core.white_border_test, images)
    logger.info("%i of %i images have white border.",
                test_results.count(True), len(test_results))
    failed = []
    # Iterate in reverse to avoid shifting
    # the indices of the objects we want to remove
    for i, passed in reversed(list(enumerate(test_results))):
        if not passed:
            del images[i]
            failed.append(entries.pop(i))
    if failed:
        # Log the names in their original order
        failed = list(reversed(failed))
        logger.info("Skipping %i images:", len(failed))
        _log_strings([x.name for x in failed])
    logger.info(util.elapsed(start))
    logger.info("\n")


def process_images(pool, func, images, entries):
    """Erase the white backgrounds from `images` and return the new images."""
    start = time.perf_counter()
    images = pool.map(func, images)
    logger.info("Erased white background from %i images:", len(images))
    _log_strings([x.name for x in entries])
    logger.info(util.elapsed(start))
    logger.info("\n")
    return images


def save_images(pool, dst, images, entries):
    """Save `images` to disk in `dst` using the filenames in `entries`."""
    start = time.perf_counter()
    fnames = [os.path.splitext(x.name)[0] + ".png" for x in entries]
    fpaths = [os.path.join(dst, x) for x in fnames]
    pool.starmap(ski.io.imsave, zip(fpaths, images))
    logger.info("Saved %i images:", len(fpaths))
    _log_strings(fnames)
    logger.info(util.elapsed(start))
    logger.info("\n")
    return fpaths
