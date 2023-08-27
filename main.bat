@echo OFF

SETLOCAL EnableDelayedExpansion

SET CONDA=C:\Users\jaime\miniconda3\Scripts

SET PATH=%CONDA%\Scripts;%CONDA%;%PATH%

CALL activate residual
START python main.py


@echo ON