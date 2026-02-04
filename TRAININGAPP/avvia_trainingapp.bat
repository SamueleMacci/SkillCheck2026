@echo off
title Avvio TRAININGAPP

:: Attiva virtualenv
call backend_env\Scripts\activate

:: Installa dipendenze backend
pip install -r training-backend\requirements.txt

:: Avvia backend Django
start cmd /k "cd training-backend && python manage.py runserver"

:: Avvia frontend Vue
start cmd /k "cd frontend\training-frontend && npm install && npm run serve"
