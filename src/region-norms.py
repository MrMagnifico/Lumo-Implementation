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

UNSELECTED_COLOR = 1

if __name__ == "__main__":
    
    image = cv.imread(path.join(IMAGE_FILE_FOLDER, IMAGE_FILE_NAME + ".png"))
    folder = path.join("outputs", IMAGE_FILE_NAME + "-parts")
    Path(folder).mkdir(exist_ok=True)

    rows, cols = image.shape[0:2]

    regions = []
    for i in range(256):
        regions.append(np.full((rows, cols, 3), 255, dtype=np.uint8))
    amounts = np.zeros(256, dtype=np.uint32)
    regions_as_list = []
    for i in range(256):
        regions_as_list.append([])

    print(f"Splitting {IMAGE_FILE_NAME}")
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            
            # print(len(regions), image.item(i, j, 0))
            regions[image.item(i, j, 0)][i][j] = [0, 0, 0]
            amounts[image.item(i, j, 0)] += 1
            regions_as_list[image.item(i, j, 0)].append((i, j))

    print(f"Filtering regions of {IMAGE_FILE_NAME}")
    for color in range(256):
        region = regions[color]
        region_as_list = regions_as_list[color]
        noise_pixels = []

        for (i, j) in region_as_list:
            if not    ((i > 0 and region[i - 1][j][0] == 0) \
                    or (i < rows - 1 and region[i + 1][j][0] == 0) \
                    or (j > 0 and region[i][j - 1][0] == 0) \
                    or (j < cols - 1 and region[i][j + 1][0] == 0)):
                region[i][j] = [255, 255, 255]
                amounts[color] -= 1
                noise_pixels.append((i, j))

        for noise_pixel in noise_pixels:
            region_as_list.remove(noise_pixel)

    selected_colors = []
    min_amount = rows * cols / 1000
    for color in range(256):
        if amounts[color] > min_amount and (color % 10 == 0 or color == 255):
            selected_colors.append(color)

    print(f"Joining selected color regions of {IMAGE_FILE_NAME}")
    sharp = np.full((rows, cols, 3), UNSELECTED_COLOR, dtype=np.uint8)
    for selected_color in selected_colors:
        # cv.imwrite((path.join(folder, str(selected_color) + ".png")), regions[selected_color])

        for (i, j) in regions_as_list[selected_color]:
            sharp[i][j] = [selected_color for k in range(3)]


    # cv.imwrite(path.join("outputs", IMAGE_FILE_NAME + "-test.png"), out)

    # exit(0)

    pixels_to_fill = []
    for i in range(rows):
        for j in range(cols):
            if sharp[i][j][0] == UNSELECTED_COLOR:
                pixels_to_fill.append((i, j))

    print(f"Filling empty space of {IMAGE_FILE_NAME}, iteration", end=" ", flush=True)
    count = 0
    while len(pixels_to_fill) > 0:
        
        count += 1
        print(count, end=", ", flush=True)

        old_sharp = sharp.copy()
        filled_pixels = []

        for (i, j) in pixels_to_fill:

            if old_sharp[i][j][0] not in selected_colors:

                for (di, dj) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if 0 <= i + di < rows and 0 <= j + dj < cols:
                        adjecent_color = old_sharp[i + di][j + dj][0]
                        
                        if adjecent_color in selected_colors:
                            sharp[i][j] = [adjecent_color for k in range(3)]
                            regions[adjecent_color][i][j] = [0, 0, 0]

                            filled_pixels.append((i, j))
                            break

        for filled_pixel in filled_pixels:
            pixels_to_fill.remove(filled_pixel)

    print("done", flush=True)

    cv.imwrite(path.join(folder, IMAGE_FILE_NAME + "-sharp.png"), sharp)

    combined_interps = np.full((rows, cols, 3), 255, dtype=np.uint8)

    selected_colors.remove(255)

    for color in selected_colors:
        for c in selected_colors:
            if c == color:
                print(f" ->{c}<- ", end="", flush=True)
            else:
                print(f" {c} ", end="", flush=True)
        print(flush=True)
        
        cv.imwrite((path.join(folder, str(color) + ".png")), regions[color])
        subprocess.run(["venv/Scripts/python.exe", "src/edge.py", folder, str(color), IMAGE_FILE_NAME + "-parts"])
        subprocess.run(["build/Release/paper-impl.exe", folder, str(color) + "-edges", "0", "0", "0", IMAGE_FILE_NAME + "-parts"], stdout=sys.stdout)

        filter = regions[color]
        region = cv.imread(path.join(folder, str(color) + "-edges-interp.png"))

        for i in range(rows):
            for j in range(cols):
                if filter[i][j][0] == 0:
                    combined_interps[i][j] = [region.item(i, j, k) for k in range(3)]

    out_folder = "outputs"
    if len(sys.argv) > 3:
        out_folder = path.join(out_folder, sys.argv[3])
    cv.imwrite(path.join(out_folder, IMAGE_FILE_NAME + "-norms.png"), combined_interps)
