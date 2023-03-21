import sys
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange

IMAGE_FILE_FOLDER = sys.argv[1]
IMAGE_FILE_NAME     = sys.argv[2]
FILTER_FILE_FOLDER = sys.argv[3]
FILTER_FILE_NAME   = sys.argv[4]

PRE_GAUSSIAN_SIZE   = (5, 5)
POST_GAUSSIAN_SIZE  = (1, 1)

# Blue: use outline/regions

if __name__ == "__main__":
    
    image = cv.imread(path.join(IMAGE_FILE_FOLDER, IMAGE_FILE_NAME + ".png"))
    filter = cv.imread(path.join(FILTER_FILE_FOLDER, FILTER_FILE_NAME + ".png"))

    min_x = min([image.shape[0], filter.shape[0]])
    min_y = min([image.shape[1], filter.shape[1]])

    out = np.arange(min_x * min_y* 3).reshape(min_x, min_y, 3).astype(np.uint8)

    for i in trange(out.shape[0], desc=f"Filtering {IMAGE_FILE_NAME}"):
        for j in range(out.shape[1]):
            
            if filter.item(i, j, 0) == 255:
                out[i][j] = [255, 255, 255]
            else:
                for k in range(3):
                    out[i][j][k] = image.item(i, j, k)

    out = cv.GaussianBlur(out, POST_GAUSSIAN_SIZE, 0)
    out_folder = "outputs"
    if len(sys.argv) > 5:
        out_folder = path.join(out_folder, sys.argv[5])
    cv.imwrite(path.join(out_folder, IMAGE_FILE_NAME + "-filtered.png"), out)
