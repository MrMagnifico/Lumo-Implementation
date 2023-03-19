import math
import sys
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange

LINES_FILE_FOLDER = sys.argv[1]
LINES_FILE_NAME   = sys.argv[2]
BLOB_FILE_FOLDER = sys.argv[3]
BLOB_FILE_NAME   = sys.argv[4]
CONFIDENCE_FILE_FOLDER = sys.argv[5]
CONFIDENCE_FILE_NAME   = sys.argv[6]
IMAGE_FILE_NAME = sys.argv[7]

PRE_GAUSSIAN_SIZE   = (5, 5)

# Blue: use outline/regions

if __name__ == "__main__":
    # assume images start top left at same position
    lines = cv.imread(path.join(LINES_FILE_FOLDER, LINES_FILE_NAME + ".png"))
    blob = cv.imread(path.join(BLOB_FILE_FOLDER, BLOB_FILE_NAME + ".png"))
    confidence = cv.imread(path.join(CONFIDENCE_FILE_FOLDER, CONFIDENCE_FILE_NAME + ".png"))

    min_x = min([lines.shape[0], blob.shape[0], confidence.shape[0]])
    min_y = min([lines.shape[1], blob.shape[1], confidence.shape[1]])

    out = np.arange(min_x * min_y* 3).reshape(min_x, min_y, 3).astype(np.uint8)

    for i in trange(out.shape[0], desc=f"Blending {LINES_FILE_NAME} and {BLOB_FILE_NAME} with {CONFIDENCE_FILE_NAME}"):
        for j in range(out.shape[1]):

            key = confidence.item(i, j, 0) / 255

            for k in range(3):
                outline_part = blob.item(i, j, k) * key
                edges_part = lines.item(i, j, k) * (1 - key)

                out[i][j][k] = outline_part + edges_part

    out_folder = "outputs"
    if len(sys.argv) > 8:
        out_folder = path.join(out_folder, sys.argv[8])
    cv.imwrite(path.join(out_folder, IMAGE_FILE_NAME + ".png"), out)
