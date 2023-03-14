import math
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange

IMAGE_FILE_NAME     = "regions.png"
PRE_GAUSSIAN_SIZE   = (5, 5)
POST_GAUSSIAN_SIZE  = (1, 1)

if __name__ == "__main__":
    # Sobel filters
    filterx = np.array([[-1, 0, 1], 
                        [-2, 0, 2], 
                        [-1, 0, 1]], dtype=np.float32)
    filtery = np.array([[1, 2, 1], 
                        [0, 0, 0], 
                        [-1, -2, -1]], dtype=np.float32)
    
    image = cv.imread(path.join("resources", IMAGE_FILE_NAME))
    image = cv.GaussianBlur(image, PRE_GAUSSIAN_SIZE, 0)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    edges_x         = cv.filter2D(src=image, ddepth=3, kernel=filterx)
    edges_y         = cv.filter2D(src=image, ddepth=3, kernel=filtery)
    rows, cols      = edges_x.shape
    out             = np.arange(rows * cols * 3).reshape(rows, cols, 3).astype(np.uint8)

    for i in trange(rows, desc="Processing rows"):
        for j in range(cols):
            x = edges_x[i, j]
            if x > -50 and x < 50:
                x = 0
            y = edges_y[i, j]
            if y > -50 and y < 50:
                y = 0
            magn = math.sqrt(x**2 + y**2)
            if magn == 0:
                out[i][j] = [0,0,0]
            else:
                # Retard moment:
                # 128 is 0 direction
                # 1 is -1
                # 255 is 1
                # ENJOY :)
                out[i][j][0] = 0
                out[i][j][1] = 128 + 127.0*y/magn
                out[i][j][2] = 128 + 127.0*x/magn
            
    out = cv.GaussianBlur(out, POST_GAUSSIAN_SIZE, 0)
    cv.imwrite(path.join("outputs", "detected-edges.png"), out)
