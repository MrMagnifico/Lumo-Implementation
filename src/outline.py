import math
import sys
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange

IMAGE_FILE_FOLDER = sys.argv[1]
IMAGE_FILE_NAME     = sys.argv[2]
PRE_GAUSSIAN_SIZE   = (5, 5)
POST_GAUSSIAN_SIZE  = (1, 1)

# over is out of image
THRESHOLD = 220

if __name__ == "__main__":
    
    image = cv.imread(path.join(IMAGE_FILE_FOLDER, IMAGE_FILE_NAME + ".png"))
    image = cv.GaussianBlur(image, PRE_GAUSSIAN_SIZE, 0)

    for i in trange(image.shape[0], desc=f"Outlining {IMAGE_FILE_NAME}"):
        for j in range(image.shape[1]):
            
            if image.item(i, j, 0) > THRESHOLD:
                image.itemset((i, j, 0), 255)
                image.itemset((i, j, 1), 255)
                image.itemset((i, j, 2), 255)
            else:
                image.itemset((i, j, 0), 0)
                image.itemset((i, j, 1), 0)
                image.itemset((i, j, 2), 0)

    image = cv.GaussianBlur(image, POST_GAUSSIAN_SIZE, 0)
    out_folder = "outputs"
    if len(sys.argv) > 3:
        out_folder = path.join(out_folder, sys.argv[3])
    cv.imwrite(path.join(out_folder, IMAGE_FILE_NAME + "-outline.png"), image)
