@echo off

set py-exe="venv/Scripts/python.exe"
set interp-exe="build/Release/paper-impl.exe"

@REM 1: outline
@REM 2: regions
set mode=1

@REM create outline
%py-exe% src/outline.py resources cat-regions2

@REM BLOB
if %mode% == 1 (
    @REM detect edges
    %py-exe% src/edge.py outputs cat-regions2-outline

    @REM interpolate
    %interp-exe% outputs cat-regions2-outline-edges 0 0 0
) else (
    @REM region-based normals
    %py-exe% src/region-norms.py resources cat-regions2
)

@REM QUILTED LINES
(
    @REM detect edges
    %py-exe% src/edge.py resources cat-lines2
    
    @REM interpolate edges
    %interp-exe% outputs cat-lines2-edges 0 0 0
)

@REM CONFIDENCE MATTE
%interp-exe% resources cat-over-under2 255 0 0

@REM blend everyting together
if %mode% == 1 (
%py-exe% src/blend.py ^
 outputs cat-lines2-edges-interp ^
 outputs cat-regions2-outline-edges-interp ^
 outputs cat-over-under2-interp ^
 final-outline
) else (
%py-exe% src/blend.py ^
 outputs cat-lines2-edges-interp ^
 outputs cat-regions2-norms ^
 outputs cat-over-under2-interp ^
 final-regions
)

@REM filter with outline
if %mode% == 1 (
%py-exe% src/filter.py ^
 outputs final-outline ^
 outputs cat-regions2-outline
) else (
%py-exe% src/filter.py ^
 outputs final-regions ^
 outputs cat-regions2-outline
)
