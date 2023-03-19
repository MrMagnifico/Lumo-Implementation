@echo off

set py-exe="venv/Scripts/python.exe"
set interp-exe="build/Release/paper-impl.exe"

@REM create outline
%py-exe% src/outline.py resources cat-regions2

@REM detect edges
%py-exe% src/edge.py resources cat-lines2
@REM use outline \/
@REM %py-exe% src/edge.py outputs cat-regions2-outline
@REM use regions \/
%py-exe% src/edge.py resources cat-regions2

@REM interpolate
%interp-exe% outputs cat-lines2-edges 0 0 0
@REM use outline \/
@REM %interp-exe% outputs cat-regions2-outline-edges 0 0 0
@REM use regions \/
%interp-exe% outputs cat-regions2-edges 0 0 0
%interp-exe% resources cat-over-under2 255 0 0

@REM blend everyting together
@REM use outline \/
%py-exe% src/blend.py ^
 outputs cat-lines2-edges-interp ^
 outputs cat-regions2-outline-edges-interp ^
 outputs cat-over-under2-interp ^
 final-outline
@REM use regions \/
%py-exe% src/blend.py ^
 outputs cat-lines2-edges-interp ^
 outputs cat-regions2-edges-interp ^
 outputs cat-over-under2-interp ^
 final-regions

@REM filter with outline
@REM use outline \/
@REM %py-exe% src/filter.py ^
@REM  outputs final-outline ^
@REM  outputs cat-regions2-outline
@REM use regions \/
%py-exe% src/filter.py ^
 outputs final-regions ^
 outputs cat-regions2-outline