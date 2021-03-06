import os
import time
import logging
import argparse
import functools
from multiprocessing.pool import ThreadPool
import skimage as ski
import skimage.io
import more_itertools
import core
import tasks
import util

util.setup_root_logger()
logger = logging.getLogger(__name__)
ski.io.use_plugin("pil")

parser = argparse.ArgumentParser(description="Erase white backgrounds from images.")
parser.add_argument("src")
parser.add_argument("-b", "--check-border",
                    help="ensure white border before processing",
                    action="store_true")
parser.add_argument("-c", "--copy-failed",
                    help="copy and set aside images which fail border test",
                    action="store_true")
parser.add_argument("-m", "--mark-bounds",
                    help="mark boundary instead of erasing background",
                    action="store_true")
parser.add_argument("-D", "--dst",
                    help="destination dir for results (default: 'X results')",
                    default=None, metavar="")
parser.add_argument("-L", "--lum-thresh",
                    type=float,
                    help="luminosity threshold (default: 0.95)",
                    default=0.95, metavar="")
parser.add_argument("-G", "--gaussian",
                    type=float,
                    help="sigma for Gaussian filter (default: 1.0)",
                    default=1, metavar="")
parser.add_argument("-H", "--hole-thresh",
                    type=int,
                    help="hole area threshold (default: 750)",
                    default=750, metavar="")
parser.add_argument("-T", "--border-thick",
                    type=int,
                    help="thickness in pixels for border test (default: 10)",
                    default=10, metavar="")
parser.add_argument("-S", "--border-sides",
                    type=int,
                    help="min white sides to pass border test (default: 3)",
                    default=3, metavar="")
parser.add_argument("-B", "--batch-size",
                    type=int,
                    help="number of images per batch (default: 50)",
                    default=50, metavar="")
parser.add_argument("-W", "--workers",
                    type=int,
                    help="number of threads to create (default: CPU count)",
                    default=os.cpu_count() or 1, metavar="")
args = parser.parse_args()

if not os.path.isdir(args.src):
    raise ValueError("`src` must be a directory")
args.src = os.path.abspath(args.src)
args.dst = args.dst or os.path.join(os.path.dirname(args.src),
                                    os.path.basename(args.src) + " results")
os.makedirs(args.dst, exist_ok=True)
logger.debug("Parameters:")
util.pprint_log(vars(args), logger.debug)
logger.debug("\n")
entries = sorted(os.scandir(args.src), key=lambda x: x.name)
_erase_whitebg = functools.partial(core.erase_white_background,
                                   lum_thresh=args.lum_thresh,
                                   sigma=args.gaussian,
                                   hole_thresh=args.hole_thresh,
                                   mark_bounds=args.mark_bounds)
_border_test = functools.partial(core.white_border_test,
                                 lum_thresh=args.lum_thresh,
                                 thick=args.border_thick,
                                 n_sides=args.border_sides)
done = []
if logger.level > logging.DEBUG:
    print("\n")
start = time.perf_counter()
with ThreadPool(processes=args.workers) as pool:
    for batch in more_itertools.chunked(entries, args.batch_size):
        images = tasks.load_images(pool, batch)
        if args.check_border:
            tasks.check_border(pool, _border_test, images, batch, args.copy_failed)
        images = tasks.process_images(pool, _erase_whitebg, images, batch)
        saved = tasks.save_images(pool, args.dst, images, batch)
        done.extend(saved)
logger.info("Finished processing %i images.", len(done))
logger.info(util.elapsed(start))
