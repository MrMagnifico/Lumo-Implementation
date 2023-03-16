import math
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange

IMAGE_FILE_NAME     = "cat-regions2.png"
PRE_GAUSSIAN_SIZE   = (5, 5)
POST_GAUSSIAN_SIZE  = (1, 1)
THRESHOLD = 230

if __name__ == "__main__":
    
    image = cv.imread(path.join("resources", IMAGE_FILE_NAME))
    image = cv.GaussianBlur(image, PRE_GAUSSIAN_SIZE, 0)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            
            if image.item(i, j, 0) < THRESHOLD:
                image.itemset((i, j, 0), 0)
                image.itemset((i, j, 1), 0)
                image.itemset((i, j, 2), 0)
            

    image = cv.GaussianBlur(image, POST_GAUSSIAN_SIZE, 0)
    cv.imwrite(path.join("outputs", "outline.png"), image)
