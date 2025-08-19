@echo off
echo Iniciando todos os servicos...

start "Prediction Service" cmd /k "cd prediction-service && venv\Scripts\activate && echo Rodando Prediction Service... && python app.py"

start "Persistence Service" cmd /k "cd persistence-service && venv\Scripts\activate && echo Rodando Persistence Service... && python app.py"

start "Dashboard Service" cmd /k "cd dashboard-service && venv\Scripts\activate && echo Rodando Dashboard Service... && python app.py"

start "Ingestion Service" cmd /k "cd ingestion-service && venv\Scripts\activate && echo Rodando Ingestion Service... && python app.py"

echo Servicos iniciados em janelas separadas.
