import math
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange

PRE_GAUSSIAN_SIZE   = (5, 5)
POST_GAUSSIAN_SIZE  = (1, 1)

# Blue: use outline

if __name__ == "__main__":
    # assume images start top left at same position
    lines = cv.imread(path.join("outputs", "lines-edges-interp.png"))
    outline = cv.imread(path.join("outputs", "outline-edges-interp.png"))
    # regions = cv.imread(path.join("outputs", "regions-edges-interp.png"))
    confidence = cv.imread(path.join("outputs", "confidence-matte.png"))

    keep_mask = cv.imread(path.join("outputs", "outline.png"))

    min_x = min([lines.shape[0], outline.shape[0], confidence.shape[0]])
    min_y = min([lines.shape[1], outline.shape[1], confidence.shape[1]])

    out = np.arange(min_x * min_y* 3).reshape(min_x, min_y, 3).astype(np.uint8)

    for i in trange(out.shape[0], desc="Processing rows"):
        for j in range(out.shape[1]):
            
            if keep_mask.item(i, j, 0) == 255:
                out[i][j] = [255, 255, 255]
                continue

            key = confidence.item(i, j, 0) / 255

            for k in range(3):
                outline_part = outline.item(i, j, k) * key
                edges_part = lines.item(i, j, k) * (1 - key)

                out[i][j][k] = outline_part + edges_part

    out = cv.GaussianBlur(out, POST_GAUSSIAN_SIZE, 0)
    cv.imwrite(path.join("outputs", "blended-outline.png"), out)
