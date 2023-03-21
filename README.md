# Lumo Implementation
This repository contains a (partial) implementation of the techniques presented in [Lumo: Illumination for Cel Animation](http://ivizlab.sfu.ca/arya/Papers/ACM/NPAR-02/Illumination%20for%20Cel%20Animation.pdf) which are used to generate normals for 2D drawings to allow them to be rendered using typical computer graphics techniques. This implementation is part of the requirements for the paper presentation assignment for the course IN4152 3D Computer Graphics and Animation at TU Delft

## Usage
The script `pipeline.bat` can be used to run the full processing pipeline on Windows machines. The variable `mode` within the file can be used to control whether blob normals or region normals are used for the blending stage (as the second contributor in addition to the edge normals)

## Group Members
- Nikolay Blagoev
- Tobias van den Hurk
- William Narchi

## Dependencies
This project makes use of a modified version of the final project framework for the course CS4365 Applied Image Processing. In addition to the Python libraries specified in `requirements.txt`, it also makes use of the following C++ libraries. Lastly, a compiler with OpenMP support (>= 2.0) is required to compile the C++ code in this project

- [GLM](https://github.com/g-truc/glm)
- [stb](https://github.com/nothings/stb)
- [progressbar](https://github.com/gipert/progressbar)
