@echo OFF

SETLOCAL EnableDelayedExpansion

SET CONDA=C:\Users\%USERNAME%\miniconda3\Scripts

SET PATH=%CONDA%\Scripts;%CONDA%;%PATH%

rem logiciel and residual environment << local solution
CALL activate logiciel && (
	echo sucess
) || (
	echo error ... searching another environment
	CALL activate residual
)

START pythonw main.py

@echo ON