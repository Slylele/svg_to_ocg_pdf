@echo off
color f5
Title Execution du Script qui transforme le fichier SVG en PDG
cls

REM Récupère le chemin du dossier où se trouve ce fichier .bat
set "BAT_DIR=%~dp0"
REM Supprime le dernier antislash si présent
if "%BAT_DIR:~-1%"=="\" set "BAT_DIR=%BAT_DIR:~0,-1%"


echo ********************************************************************
echo *     Saisir le nom du fichier SVG                                 *
echo *     Si vous laissez vide, il prendra la valeur par defaut        *
echo *     par defaut : Test_exemple.svg                                *
echo ********************************************************************
REM Demande le nom du fichier SVG à l'utilisateur
set /p SVG_FILE=Nom du fichier SVG :
REM Si l'utilisateur n'a rien saisi, utiliser la valeur par défaut
if "%SVG_FILE%"=="" set "SVG_FILE=Test_exemple.svg"


@echo off
REM Exécute le script Python avec le chemin du .bat comme 1er argument
python "C:\Applis\svg_to_ocg_pdf\svg_to_ocg_pdf.py" "%BAT_DIR%" "%SVG_FILE%"
exit