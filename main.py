import os
import logging
import argparse
import skimage as ski
import skimage.io
import win_unicode_console
from image import erase_white_background
import util

win_unicode_console.streams.enable()
util.setup_root_logger()
logger = logging.getLogger(__name__)
ski.io.use_plugin("imageio")

parser = argparse.ArgumentParser(description="Erase white backgrounds from images.")
parser.add_argument("src")
parser.add_argument("--dst",
                    help="destination directory for results",
                    default=None)
parser.add_argument("--thresh",
                    type=float,
                    help="luminosity threshold above which is white",
                    default=0.95)
parser.add_argument("--blur",
                    type=float,
                    help="sigma for Gaussian filter (higher for more blur)",
                    default=1)
parser.add_argument("--hole",
                    type=int,
                    help="ignore holes below this area threshold",
                    default=750)
args = parser.parse_args()

if not os.path.isdir(args.src):
    raise ValueError("`src` must be a directory")
args.src = os.path.abspath(args.src)
args.dst = args.dst or os.path.join(os.path.dirname(args.src),
                                    os.path.basename(args.src) + " results")
os.makedirs(args.dst, exist_ok=True)
logger.debug("src: %s", args.src)
logger.debug("dst: %s", args.dst)

for entry in os.scandir(args.src):
    img = ski.io.imread(entry.path)
    logger.debug("Loaded %s.", entry.name)
    img = erase_white_background(img, thresh=args.thresh, sigma=args.blur, hole_thresh=args.hole)
    logger.debug("Erased white background from %s.", entry.name)
    fpath = os.path.join(args.dst, os.path.splitext(entry.name)[0] + ".png")
    ski.io.imsave(fpath, img)
    logger.debug("Saved image as %s.", os.path.basename(fpath))
