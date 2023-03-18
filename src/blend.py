import math
import sys
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange

LINES_FILE_FOLDER = sys.argv[1]
LINES_FILE_NAME   = sys.argv[2]
OUTLINE_FILE_FOLDER = sys.argv[3]
OUTLINE_FILE_NAME   = sys.argv[4]
CONFIDENCE_FILE_FOLDER = sys.argv[5]
CONFIDENCE_FILE_NAME   = sys.argv[6]
IMAGE_FILE_NAME = sys.argv[7]

PRE_GAUSSIAN_SIZE   = (5, 5)
POST_GAUSSIAN_SIZE  = (1, 1)

# Blue: use outline/regions

if __name__ == "__main__":
    # assume images start top left at same position
    lines = cv.imread(path.join(LINES_FILE_FOLDER, LINES_FILE_NAME + ".png"))
    outline = cv.imread(path.join(OUTLINE_FILE_FOLDER, OUTLINE_FILE_NAME + ".png"))
    # regions = cv.imread(path.join("outputs", "regions-edges-interp.png"))
    confidence = cv.imread(path.join(OUTLINE_FILE_FOLDER, OUTLINE_FILE_NAME + ".png"))

    min_x = min([lines.shape[0], outline.shape[0], confidence.shape[0]])
    min_y = min([lines.shape[1], outline.shape[1], confidence.shape[1]])

    out = np.arange(min_x * min_y* 3).reshape(min_x, min_y, 3).astype(np.uint8)

    for i in trange(out.shape[0], desc=f"Blending {LINES_FILE_NAME} and {OUTLINE_FILE_NAME} with {CONFIDENCE_FILE_NAME}"):
        for j in range(out.shape[1]):

            key = confidence.item(i, j, 0) / 255

            for k in range(3):
                outline_part = outline.item(i, j, k) * key
                edges_part = lines.item(i, j, k) * (1 - key)

                out[i][j][k] = outline_part + edges_part

    out = cv.GaussianBlur(out, POST_GAUSSIAN_SIZE, 0)
    cv.imwrite(path.join("outputs", IMAGE_FILE_NAME + ".png"), out)
