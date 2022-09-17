@echo off
title Rat Builder
chcp 65001 >nul
:builder
cls
echo [40;34m
ping localhost -n 1 >nul & echo.
ping localhost -n 1 >nul & echo     ██▀███   ▄▄▄     ▄▄▄█████▓    ▄▄▄▄    █    ██  ██▓ ██▓    ▓█████▄ ▓█████  ██▀███  
ping localhost -n 1 >nul & echo    ▓██ ▒ ██▒▒████▄   ▓  ██▒ ▓▒   ▓█████▄  ██  ▓██▒▓██▒▓██▒    ▒██▀ ██▌▓█   ▀ ▓██ ▒ ██▒
ping localhost -n 1 >nul & echo    ▓██ ░▄█ ▒▒██  ▀█▄ ▒ ▓██░ ▒░   ▒██▒ ▄██▓██  ▒██░▒██▒▒██░    ░██   █▌▒███   ▓██ ░▄█ ▒
ping localhost -n 1 >nul & echo    ▒██▀▀█▄  ░██▄▄▄▄██░ ▓██▓ ░    ▒██░█▀  ▓▓█  ░██░░██░▒██░    ░▓█▄   ▌▒▓█  ▄ ▒██▀▀█▄  
ping localhost -n 1 >nul & echo    ░██▓ ▒██▒ ▓█   ▓██▒ ▒██▒ ░    ░▓█  ▀█▓▒▒█████▓ ░██░░██████▒░▒████▓ ░▒████▒░██▓ ▒██▒
ping localhost -n 1 >nul & echo    ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ▒ ░░      ░▒▓███▀▒░▒▓▒ ▒ ▒ ░▓  ░ ▒░▓  ░ ▒▒▓  ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
ping localhost -n 1 >nul & echo      ░▒ ░ ▒░  ▒   ▒▒ ░   ░       ▒░▒   ░ ░░▒░ ░ ░  ▒ ░░ ░ ▒  ░ ░ ▒  ▒  ░ ░  ░  ░▒ ░ ▒░
ping localhost -n 1 >nul & echo      ░░   ░   ░   ▒    ░          ░    ░  ░░░ ░ ░  ▒ ░  ░ ░    ░ ░  ░    ░     ░░   ░ 
ping localhost -n 1 >nul & echo       ░           ░  ░            ░         ░      ░      ░  ░   ░       ░  ░   ░     
ping localhost -n 1 >nul & echo                                       ░                       ░                      
ping localhost -n 1 >nul & echo.
ping localhost -n 1 >nul & set /p input="[40;37m[[40;32mPANEL[40;37m] [40;34m>>>[40;32m "
if not exist rat.py echo rat.py wasnt found! & ping localhost -n 3 >nul & goto builder
if %input% == build goto setup
goto builder

:setup
echo [40;37m
set /p input2="[[40;32mNAME[40;37m] What do you want the file name to be? [40;34m>>>[40;32m "
goto setup2

:setup2
echo [40;37m
set /p input3="[[40;32mADDON[40;37m] Want to add a icon to the rat? [40;34m>>>[40;32m "
if %input3% == yes goto setup4
if %input3% == no goto setup3
goto builder

:setup3
echo [40;37m
set /p input4="[[40;32mADDON[40;37m] Want to add force admin to the rat? [40;34m>>>[40;32m "
if %input4% == yes goto build
if %input4% == no goto build2
goto builder

:setup4
echo [40;37m
set /p input5="[[40;32mICON[40;37m] Drag and drop the ico file inside the rat builder [40;34m>>>[40;32m "
goto setup5

:setup5
echo [40;37m
set /p input6="[[40;32mADDON[40;37m] Want to add force admin to the rat? [40;34m>>>[40;32m "
if %input6% == yes goto build3
if %input6% == no goto build4
goto builder

:build
echo [40;37m[[40;32m![40;37m] Starting builder, please wait!
ping localhost -n 3 >nul
pyinstaller --clean --onefile --uac-admin -w rat.py
ren dist\rat.exe %input2%.exe
del rat.spec >nul
echo [[40;32m+[40;37m] Done
ping localhost -n 3 >nul
pause
goto builder

:build2
echo [40;37m[[40;32m![40;37m] Starting builder, please wait!
ping localhost -n 3 >nul
pyinstaller --clean --onefile -w rat.py
ren dist\rat.exe %input2%.exe
del rat.spec >nul
echo [[40;32m+[40;37m] Done
ping localhost -n 3 >nul
pause
goto builder

:build3
echo [40;37m[[40;32m![40;37m] Starting builder, please wait!
ping localhost -n 3 >nul
pyinstaller --clean --onefile --uac-admin -w -i %input5% rat.py
ren dist\rat.exe %input2%.exe
del rat.spec >nul
echo [[40;32m+[40;37m] Done
ping localhost -n 3 >nul
pause
goto builder

:build4
echo [40;37m[[40;32m![40;37m] Starting builder, please wait!
ping localhost -n 3 >nul
pyinstaller --clean --onefile -w -i %input5% rat.py
ren dist\rat.exe %input2%.exe
del rat.spec >nul
echo [[40;32m+[40;37m] Done
ping localhost -n 3 >nul
pause
goto builder