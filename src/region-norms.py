import math
from pathlib import Path
import sys
import numpy as np
import cv2 as cv
from os import path
from tqdm import trange, tqdm
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

    out = np.full((rows, cols, 3), 255, dtype=np.uint8)

    selected_colors = []
    # ignore white background
    for color in range(255):
        if amounts[color] > min_amount:
            selected_colors.append(color)

    for color in tqdm(selected_colors, desc=f"Adding to result"):
        # cv.imwrite((path.join(folder, str(i) + ".png")), regions[color])
        # subprocess.run(["venv/Scripts/python.exe", "src/edge.py", folder, str(color), IMAGE_FILE_NAME + "-parts"])
        # subprocess.run(["build/Release/paper-impl.exe", folder, str(color) + "-edges", "0", "0", "0", IMAGE_FILE_NAME + "-parts"], stdout=sys.stdout)

        filter = regions[color]
        region = cv.imread(path.join(folder, str(color) + "-edges-interp.png"))

        for i in range(rows):
            for j in range(cols):
                if filter[i][j][0] == 0:
                    for k in range(3):
                        out[i][j][k] = region.item(i, j, k)

    out_folder = "outputs"
    if len(sys.argv) > 3:
        out_folder = path.join(out_folder, sys.argv[3])
    cv.imwrite(path.join(out_folder, IMAGE_FILE_NAME + "-norms.png"), out)
