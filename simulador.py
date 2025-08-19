# simulador.py
import requests
import time
import os
import json

# URL do seu serviço de ingestão. Verifique se a porta está correta!
INGESTION_API_URL = "http://127.0.0.1:8000/ingest"

# Nomes das colunas na ordem em que aparecem no arquivo .txt da NASA
COLUMN_NAMES = [
    'unit_number', 'time_in_cycles', 'op_setting_1', 'op_setting_2', 'op_setting_3',
    'sensor_1', 'sensor_2', 'sensor_3', 'sensor_4', 'sensor_5', 'sensor_6',
    'sensor_7', 'sensor_8', 'sensor_9', 'sensor_10', 'sensor_11', 'sensor_12',
    'sensor_13', 'sensor_14', 'sensor_15', 'sensor_16', 'sensor_17', 'sensor_18',
    'sensor_19', 'sensor_20', 'sensor_21'
]

# --- MODIFICAÇÃO PARA TESTE ---
# Vamos simular apenas os 5 primeiros motores para garantir que a predição aconteça.
MOTORES_PARA_SIMULAR = 5

def parse_line_to_json(line: str):
    """Converte uma linha do arquivo .txt para um dicionário JSON com tipos corretos."""
    parts = line.strip().split()
    data = {}
    for i, name in enumerate(COLUMN_NAMES):
        # Os dois primeiros (unit_number, time_in_cycles) são inteiros
        if i < 2:
            data[name] = int(parts[i])
        # O resto são floats
        else:
            data[name] = float(parts[i])
    return data

def run_simulation(data_file_path: str):
    """Lê o arquivo de dados e envia cada linha para a API de ingestão."""
    
    if not os.path.exists(data_file_path):
        print(f"ERRO: Arquivo de dados não encontrado em '{data_file_path}'")
        return

    print(f"Iniciando simulação com dados de '{data_file_path}'...")
    print(f"Enviando dados para: {INGESTION_API_URL}")
    print(f"--- MODO DE TESTE: Simulando apenas os primeiros {MOTORES_PARA_SIMULAR} motores. ---")


    with open(data_file_path, 'r') as f:
        for i, line in enumerate(f):
            # Converte a linha para o formato JSON que a API espera
            payload = parse_line_to_json(line)
            
            # --- LÓGICA DO MODO DE TESTE ---
            # Pula para a próxima linha se o motor não estiver na nossa lista de teste
            if payload['unit_number'] > MOTORES_PARA_SIMULAR:
                continue 
            
            try:
                # O FastAPI espera o payload no parâmetro 'json' do requests
                response = requests.post(INGESTION_API_URL, json=payload)
                
                if response.status_code == 202:
                    unit = payload['unit_number']
                    cycle = payload['time_in_cycles']
                    print(f"Registro {i+1}: Motor {unit}, Ciclo {cycle} -> Enviado com sucesso!")
                else:
                    print(f"Erro ao enviar registro {i+1}: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                print("\nERRO DE CONEXÃO: Não foi possível conectar ao 'ingestion-service'.")
                print("Verifique se o serviço está rodando na porta 8000.")
                break
            
            # Pausa para simular dados chegando em tempo real e não sobrecarregar
            time.sleep(0.1)

    print("\nSimulação concluída!")

if __name__ == "__main__":
    # Verifique se este caminho está correto para a localização do seu arquivo
    dataset_path = "train_FD001.txt" 
    run_simulation(dataset_path)