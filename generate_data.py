import requests
import json
import time
import random
import uuid
from datetime import datetime, timezone

# URL do nosso serviço de ingestão
INGESTION_API_URL = "http://127.0.0.1:8000/ingest"

def generate_sensor_data():
    """Gera um único ponto de dado de sensor com um estado aleatório."""

    # Escolhe um estado aleatório para o dado
    state = random.choices(['SAUDAVEL', 'ALERTA', 'CRITICO'], weights=[0.85, 0.10, 0.05], k=1)[0]

    temp = 0.0
    vibe = 0.0

    if state == 'SAUDAVEL':
        temp = random.uniform(20.0, 69.9)
        vibe = random.uniform(0.5, 4.9)
    elif state == 'ALERTA':
        temp = random.uniform(70.0, 89.9)
        vibe = random.uniform(5.0, 9.9)
    elif state == 'CRITICO':
        temp = random.uniform(90.0, 110.0)
        vibe = random.uniform(10.0, 15.0)

    return {
        "sensor_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(temp, 2),
        "vibration": round(vibe, 2)
    }

def run_simulation(record_count=1000):
    """Executa a simulação, enviando dados para a API."""

    print(f"Iniciando simulação para gerar {record_count} registros...")

    for i in range(record_count):
        data = generate_sensor_data()

        try:
            response = requests.post(INGESTION_API_URL, data=json.dumps(data), headers={'Content-Type': 'application/json'})

            if response.status_code == 202:
                print(f"Registro {i+1}/{record_count} enviado com sucesso: Temp={data['temperature']}, Vib={data['vibration']}")
            else:
                print(f"Erro ao enviar registro {i+1}: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError as e:
            print("\nERRO: Não foi possível conectar ao serviço de ingestão.")
            print("Por favor, certifique-se de que o 'ingestion-service' está rodando na porta 8000.")
            break

        # Pequeno delay para não sobrecarregar os serviços
        time.sleep(0.5)

    print("\nSimulação concluída!")


if __name__ == "__main__":
    # Antes de rodar, certifique-se de que todos os seus serviços estão no ar!
    # (ingestion-service, prediction-service, persistence-service)
    run_simulation(1000)