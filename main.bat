@echo OFF

SETLOCAL EnableDelayedExpansion

SET CONDA=C:\Users\%USERNAME%\miniconda3\Scripts

SET PATH=%CONDA%\Scripts;%CONDA%;%PATH%

CALL activate logiciel
START python main.py


@echo ON