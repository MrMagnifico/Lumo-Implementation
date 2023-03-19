import math
from pathlib import Path
import sys
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange
import subprocess

IMAGE_FILE_FOLDER = sys.argv[1]
IMAGE_FILE_NAME     = sys.argv[2]

# over is out of image
THRESHOLD = 220

if __name__ == "__main__":
    
    image = cv.imread(path.join(IMAGE_FILE_FOLDER, IMAGE_FILE_NAME + ".png"))

    rows, cols = image.shape[0:2]
    min_amount = rows * cols / 100

    regions = []
    amounts = np.zeros(256, dtype=np.uint32)
    for i in range(256):
        regions.append(np.full((rows, cols, 3), 255, dtype=np.uint8))

    for i in trange(image.shape[0], desc=f"Splitting {IMAGE_FILE_NAME}"):
        for j in range(image.shape[1]):
            
            regions[image.item(i, j, 0)][i][j] = [0, 0, 0]
            amounts[image.item(i, j, 0)] += 1

    folder = path.join("outputs", IMAGE_FILE_NAME + "-parts")
    Path(folder).mkdir(exist_ok=True)

    # ignore white background
    for i in range(255):
        if amounts[i] > min_amount:
            cv.imwrite((path.join(folder, str(i) + ".png")), regions[i])
            subprocess.run(["venv/Scripts/python.exe", "src/edge.py", folder, str(i), IMAGE_FILE_NAME + "-parts"])
            subprocess.run(["build/Release/paper-impl.exe", folder, str(i) + "-edges", "0", "0", "0", IMAGE_FILE_NAME + "-parts"], stdout=sys.stdout)
