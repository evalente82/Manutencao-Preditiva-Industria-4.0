# prediction-service/app/service.py

import os
import json
import logging
import joblib
import pandas as pd
import numpy as np
import tensorflow as tf
from confluent_kafka import Consumer, Producer, KafkaException
from dotenv import load_dotenv

# --- CONFIGURAÇÕES ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# O tamanho da sequência que o modelo LSTM espera
TIME_STEPS = 10

# --- CARREGAR O ESCALONADOR E O MODELO DE ML ---
try:
    scaler = joblib.load("scaler.pkl")
    logger.info("Escalonador (scaler.pkl) carregado com sucesso.")
    # Carregar o modelo Keras/TensorFlow
    model = tf.keras.models.load_model('rul_prediction_model.h5')
    logger.info("Modelo Keras (rul_prediction_model.h5) carregado com sucesso.")
except Exception as e:
    logger.error(f"ERRO CRÍTICO ao carregar modelos: {e}")
    logger.error("Verifique se 'scaler.pkl' e 'rul_prediction_model.h5' estão na pasta 'prediction-service'.")
    exit()

# --- CONFIGURAÇÃO KAFKA ---
KAFKA_CONSUMER_TOPIC = "sensor-data"
KAFKA_PRODUCER_TOPIC = "prediction-results"
kafka_config = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL', 'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_API_KEY'), 'sasl.password': os.getenv('KAFKA_API_SECRET'),
}
consumer_config = kafka_config.copy()
consumer_config.update({'group.id': 'prediction-lstm-service-group-1', 'auto.offset.reset': 'earliest'})
producer_config = kafka_config.copy()

# --- LÓGICA DO SERVIÇO ---
engine_histories = {} # Dicionário para guardar o histórico de cada motor

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Falha ao entregar predição: {err}")
    else:
        logger.info(f"Predição entregue ao tópico {msg.topic()}")

def run_service():
    consumer = Consumer(consumer_config)
    producer = Producer(producer_config)
    consumer.subscribe([KAFKA_CONSUMER_TOPIC])
    logger.info("Serviço de predição (LSTM) iniciado. Aguardando dados...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error(): raise KafkaException(msg.error())

            data = json.loads(msg.value().decode('utf-8'))
            unit_number = data.get('unit_number')
            logger.info(f"Dado recebido do motor: {unit_number}, ciclo: {data.get('time_in_cycles')}")

            # Organizar os dados recebidos na ordem correta das features
            feature_columns = [
                'op_setting_1', 'op_setting_2', 'op_setting_3', 'sensor_1', 'sensor_2', 'sensor_3', 
                'sensor_4', 'sensor_5', 'sensor_6', 'sensor_7', 'sensor_8', 'sensor_9', 'sensor_10',
                'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 'sensor_16',
                'sensor_17', 'sensor_18', 'sensor_19', 'sensor_20', 'sensor_21'
            ]
            input_data = {col: [data.get(col)] for col in feature_columns}
            input_df = pd.DataFrame(input_data)

            # Escalonar os novos dados
            scaled_data = scaler.transform(input_df)

            # Atualizar o histórico do motor
            if unit_number not in engine_histories:
                engine_histories[unit_number] = []
            
            engine_histories[unit_number].append(scaled_data[0])

            # Manter o histórico com o tamanho máximo da sequência
            if len(engine_histories[unit_number]) > TIME_STEPS:
                engine_histories[unit_number].pop(0)
            
            # Fazer a predição APENAS se tivermos a sequência completa
            if len(engine_histories[unit_number]) == TIME_STEPS:
                # 1. Preparar a sequência para o modelo
                input_sequence = np.array(engine_histories[unit_number])
                input_sequence = input_sequence.reshape(1, TIME_STEPS, len(feature_columns))

                # 2. Fazer a predição
                rul_prediction = model.predict(input_sequence)[0][0]
                logger.info(f"PREDIÇÃO DE RUL para motor {unit_number}: {rul_prediction}")
                
                # 3. Publicar o resultado
                prediction_payload = data.copy()
                prediction_payload['RUL'] = int(rul_prediction)
                
                producer.produce(
                    KAFKA_PRODUCER_TOPIC,
                    key=str(unit_number),
                    value=json.dumps(prediction_payload).encode('utf-8'),
                    callback=delivery_report
                )
                producer.poll(0)

    except KeyboardInterrupt:
        logger.info("Serviço de predição (LSTM) interrompido.")
    finally:
        consumer.close()
        producer.flush()

if __name__ == "__main__":
    run_service()