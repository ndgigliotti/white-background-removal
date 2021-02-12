import os
import logging
import argparse
import functools
import timeit
from multiprocessing.pool import ThreadPool
import skimage as ski
import skimage.io
from more_itertools import chunked
from image import erase_white_background, white_border_test
import util

util.setup_root_logger()
logger = logging.getLogger(__name__)
ski.io.use_plugin("pil")

parser = argparse.ArgumentParser(description="Erase white backgrounds from images.")
parser.add_argument("src")
parser.add_argument("--check-border",
                    help="ensure white border before processing",
                    action="store_true")
parser.add_argument("--dst",
                    help="destination directory for results",
                    default=None)
parser.add_argument("--lum",
                    type=float,
                    help="luminosity threshold (default: 0.95)",
                    default=0.95)
parser.add_argument("--blur",
                    type=float,
                    help="sigma for Gaussian filter (default: 1.0)",
                    default=1)
parser.add_argument("--hole",
                    type=int,
                    help="hole area threshold (default: 750)",
                    default=750)
parser.add_argument("--batch",
                    type=int,
                    help="batch size (default: 20)",
                    default=20)
parser.add_argument("--workers",
                    type=int,
                    help="number of workers for multithreading (default: CPU count)",
                    default=os.cpu_count() or 1)
args = parser.parse_args()

if not os.path.isdir(args.src):
    raise ValueError("`src` must be a directory")
args.src = os.path.abspath(args.src)
args.dst = args.dst or os.path.join(os.path.dirname(args.src),
                                    os.path.basename(args.src) + " results")
os.makedirs(args.dst, exist_ok=True)

entries = sorted(os.scandir(args.src), key=lambda x: x.name)
_erase = functools.partial(erase_white_background, lum_thresh=args.lum,
                           sigma=args.blur, hole_thresh=args.hole)

start = timeit.default_timer()
count = 0
print("\n")
with ThreadPool(processes=args.workers) as pool:
    for chunk in chunked(entries, args.batch):
        imgs = pool.map(ski.io.imread, [x.path for x in chunk])
        logger.info("Loaded %i images:", len(imgs))
        logger.info([x.name for x in chunk])
        logger.info("\n")
        if args.check_border:
            white_border = pool.map(white_border_test, imgs)
            imgs = [x for x, y in zip(imgs, white_border) if y]
            failed = [x for x, y in zip(chunk, white_border) if not y]
            chunk = [x for x in chunk if x not in failed]
            logger.info("%i of %i images have white border.",
                        white_border.count(True), len(white_border))
            if failed:
                logger.info("Skipping %i images:", len(failed))
                logger.info([x.name for x in failed])
            logger.info("\n")
        imgs = pool.map(_erase, imgs)
        logger.info("Erased white background from %i images:", len(imgs))
        logger.info([x.name for x in chunk])
        logger.info("\n")
        fpaths = [os.path.join(args.dst, os.path.splitext(x.name)[0] + ".png") for x in chunk]
        pool.starmap(ski.io.imsave, zip(fpaths, imgs))
        logger.info("Saved %i images:", len(fpaths))
        logger.info([os.path.basename(x) for x in fpaths])
        logger.info("\n")
        count += len(imgs)
logger.info("Finished processing %i images. Took %s.", count, util.elapsed(start))
