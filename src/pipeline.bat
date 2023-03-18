@echo off

set py-exe="venv/Scripts/python.exe"
set interp-exe="build/Release/paper-impl.exe"

%py-exe% src/outline.py resources cat-regions2
%py-exe% src/edge.py  resources cat-lines2
%py-exe% src/edge.py outputs cat-regions2-outline
%interp-exe% outputs cat-lines2-edges 0 0 0
%interp-exe% outputs cat-regions2-outline-edges 0 0 0
%interp-exe% resources cat-over-under2 255 0 0
%py-exe% src/blend.py outputs ^
 cat-lines2-edges-interp ^
 outputs cat-regions2-outline-edges-interp ^
 outputs cat-over-under2-interp ^
 final
%py-exe% src/filter.py ^
 outputs final ^
 outputs cat-regions2-outline