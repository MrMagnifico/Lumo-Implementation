import math
import numpy as np
import cv2 as cv
filterx = np.array([[-1, 0, 1], 
                    [-2, 0, 2], 
                    [-1, 0, 1]], dtype=np.float32)

filtery = np.array([[-1, -2, -1], 
                    [0, 0, 0], 
                    [1, 2, 1]], dtype=np.float32)
image = cv.imread("out2.png")
image = cv.GaussianBlur(image,(5,5),0)
image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

edgesx = cv.filter2D(src=image, ddepth = 3, kernel=filterx*-1)
edgesy = cv.filter2D(src=image, ddepth = 3, kernel=filtery*-1)
rows,cols = edgesx.shape
out = np.arange((rows)*(cols)*3).reshape((rows),(cols), 3).astype(np.uint8)
out2 = np.arange((rows)*(cols)*2).reshape((rows),(cols), 2).astype(np.float32)
for i in range(rows):
    for j in range(cols):
        x = edgesx[i,j]
        if x > -50 and x < 50:
            x = 0
        y = edgesy[i,j]
        if y > -50 and y < 50:
            y = 0
        magn = math.sqrt(x**2+y**2)
        if magn == 0:
            out[i][j] = [0,0,0]
        else:
            # Retard moment:
            # 123 is 0 direction
            # 1 is -1
            # 255 is 1
            # ENJOY :)
            print(123 + 122.0*x/magn, 123 + 122.0*y/magn, x, y)
            out[i][j][0] = 0
            out[i][j][1] = 123 + 122.0*y/magn
            out[i][j][2] = 123 + 122.0*x/magn
            out2[i][j][0] = y/magn
            out2[i][j][1] = x/magn
        

cv.imwrite('edgesb.png', out)
exit()