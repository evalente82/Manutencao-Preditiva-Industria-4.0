# simulador_continuo.py
import requests
import time
import random
import json
import websocket
import threading

# --- CONFIGURAÇÕES ---
INGESTION_API_URL = "http://127.0.0.1:8000/ingest"
DASHBOARD_API_URL = "127.0.0.1:8001"
NUM_MOTORES = 3
estado_simulacao = {"rodando": False}

# --- ESTADO DOS MOTORES (agora no escopo global para ser resetado) ---
motores_estado = {}

def resetar_estado_motores():
    """Zera o estado de todos os motores para o início."""
    global motores_estado
    motores_estado = {
        unit: {"time_in_cycles": 0, "desgaste": 0.0}
        for unit in range(1, NUM_MOTORES + 1)
    }

# --- LÓGICA DE WEBSOCKET (para logs e controle) ---
log_ws_client = None

def conectar_log_ws():
    global log_ws_client
    try:
        log_ws_client = websocket.create_connection(f"ws://{DASHBOARD_API_URL}/ws/sim_logs")
        print("SIMULADOR: Conectado ao WebSocket de logs.")
    except Exception as e:
        print(f"SIMULADOR: Não foi possível conectar ao WebSocket de logs: {e}")
        log_ws_client = None

def enviar_log(mensagem):
    global log_ws_client
    print(f"LOG: {mensagem}")
    if log_ws_client:
        try:
            log_ws_client.send(mensagem)
        except Exception:
            conectar_log_ws()
            if log_ws_client:
                try:
                    log_ws_client.send(mensagem)
                except Exception as e:
                    print(f"SIMULADOR: Falha ao reenviar log: {e}")

def ouvir_comandos_controle():
    global estado_simulacao
    ws_url = f"ws://{DASHBOARD_API_URL}/ws/sim_control"
    while True:
        try:
            ws = websocket.create_connection(ws_url)
            print("SIMULADOR: Conectado ao WebSocket de controle. Aguardando comandos.")
            while True:
                comando = ws.recv()
                if comando == "START":
                    estado_simulacao["rodando"] = True
                    enviar_log("--- SIMULAÇÃO INICIADA ---")
                elif comando == "STOP":
                    estado_simulacao["rodando"] = False
                    resetar_estado_motores() # <-- AQUI ESTÁ A NOVA LÓGICA
                    enviar_log("--- SIMULAÇÃO FINALIZADA E REINICIADA ---")
        except Exception as e:
            print(f"SIMULADOR: Conexão de controle perdida: {e}. Tentando reconectar em 5s...")
            time.sleep(5)

# --- LÓGICA DE GERAÇÃO DE DADOS (sem alterações) ---
def gerar_dados_motor(unit_number, estado):
    estado["time_in_cycles"] += 1
    estado["desgaste"] += random.uniform(0.0001, 0.0005)
    desgaste = estado["desgaste"]
    payload = {
        "unit_number": unit_number, "time_in_cycles": estado["time_in_cycles"],
        "op_setting_1": round(random.uniform(-0.005, 0.005) + desgaste * 0.1, 4),
        "op_setting_2": round(random.uniform(-0.0002, 0.0002), 4), "op_setting_3": 100.0,
        "sensor_1": 518.67, "sensor_2": round(641.82 + random.uniform(-0.5, 0.5) + desgaste * 15, 2),
        "sensor_3": round(1583.1 + random.uniform(-2, 2) + desgaste * 10, 2),
        "sensor_4": round(1398.9 + random.uniform(-2, 2) + desgaste * 25, 2), "sensor_5": 14.62,
        "sensor_6": 21.61, "sensor_7": round(554.0 + random.uniform(-0.5, 0.5) - desgaste * 10, 2),
        "sensor_8": 2388.05, "sensor_9": round(9055.0 + random.uniform(-5, 5) + desgaste * 100, 2),
        "sensor_10": 1.3, "sensor_11": round(47.35 + random.uniform(-0.2, 0.2) + desgaste * 5, 2),
        "sensor_12": round(522.0 + random.uniform(-0.5, 0.5) - desgaste * 10, 2), "sensor_13": 2388.08,
        "sensor_14": round(8140.0 + random.uniform(-2, 2) + desgaste * 50, 2),
        "sensor_15": round(8.4 + random.uniform(-0.05, 0.05) + desgaste * 0.1, 4), "sensor_16": 0.03,
        "sensor_17": round(391 + random.uniform(-1, 1) + desgaste * 5, 0), "sensor_18": 2388,
        "sensor_19": 100.0, "sensor_20": round(38.8 + random.uniform(-0.1, 0.1) - desgaste * 2, 2),
        "sensor_21": round(23.3 + random.uniform(-0.1, 0.1) - desgaste * 2, 4)
    }
    return estado, payload

def run_simulation():
    motor_atual = 1
    while True:
        try:
            if estado_simulacao["rodando"]:
                estado_atual, payload = gerar_dados_motor(motor_atual, motores_estado[motor_atual])
                requests.post(INGESTION_API_URL, json=payload)
                log_msg = f"Motor {payload['unit_number']}, Ciclo {payload['time_in_cycles']} -> Dados enviados."
                enviar_log(log_msg)
                motor_atual = (motor_atual % NUM_MOTORES) + 1
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            enviar_log("ERRO: Ingestion-service indisponível. Tentando em 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            if log_ws_client: log_ws_client.close()
            break

if __name__ == "__main__":
    resetar_estado_motores() # Garante que o estado comece zerado
    conectar_log_ws()
    control_thread = threading.Thread(target=ouvir_comandos_controle, daemon=True)
    control_thread.start()
    enviar_log("Simulador pronto. Aguardando comando START do dashboard.")
    run_simulation()