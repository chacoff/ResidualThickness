@echo off
setlocal enabledelayedexpansion

rem ----- switch to master
git checkout master

rem ----- activate enviroment
call conda activate residual

rem ----- create buildMachine folder
mkdir buildMachine

rem ----- "compile"
python -m nuitka --standalone --windows-icon-from-ico=icons/chart.ico --windows-console-mode=disable main.py --enable-plugin=pyqt6

rem ----- copy the rest of files
mkdir "main.dist\icons"
copy "icons\logoAM.png" "main.dist\icons\logoAM.png"
copy "icons\cat.png" "main.dist\icons\cat.png"
copy "icons\chart.ico" "main.dist\icons\chart.ico"
copy "icons\chart.png" "main.dist\icons\chart.png"

rem ---- deactivate enviroment
call conda deactivate

rem ---- Compress to zip
rename "main.dist" "ResidualCorrosionApp"
powershell Compress-Archive -Path "ResidualCorrosionApp" -DestinationPath "buildMachine\ResidualCorrosionApp.zip"

rem ---- Delete folders
rmdir /s /q "main.build"
rmdir /s /q "main.dist"
rmdir /s /q "ResidualCorrosionApp"

rem ---- NSIS installer 
rem ---- $LocalAppData\Programs

