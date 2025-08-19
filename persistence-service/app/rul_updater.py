import os
import json
import logging
from confluent_kafka import Consumer, KafkaException
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import EngineData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

KAFKA_TOPIC = "prediction-results"

kafka_config = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_API_KEY'),
    'sasl.password': os.getenv('KAFKA_API_SECRET'),
    'group.id': 'persistence-group-rul-updater-1',
    'auto.offset.reset': 'earliest'
}

def process_message(msg):
    try:
        data = json.loads(msg.value().decode('utf-8'))
        logger.info(f"Predição de RUL recebida para o motor: {data.get('unit_number')}")

        db = SessionLocal()
        try:
            # Encontrar o registro existente para atualizar
            record_to_update = db.query(EngineData).filter(
                EngineData.unit_number == data.get('unit_number'),
                EngineData.time_in_cycles == data.get('time_in_cycles')
            ).first()

            if record_to_update:
                record_to_update.rul = data.get('RUL')
                db.commit()
                logger.info(f"RUL atualizada para o motor {data.get('unit_number')}, ciclo {data.get('time_in_cycles')}.")
            else:
                logger.warning(f"Registro não encontrado para motor {data.get('unit_number')}, ciclo {data.get('time_in_cycles')}. A RUL não foi salva.")
        finally:
            db.close()

    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar JSON da predição: {msg.value()}")
    except Exception as e:
        logger.error(f"Erro ao processar mensagem de predição: {e}")

def run_rul_updater():
    consumer = Consumer(kafka_config)
    consumer.subscribe([KAFKA_TOPIC])
    logger.info(f"Atualizador de RUL iniciado no tópico '{KAFKA_TOPIC}'. Aguardando predições...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                process_message(msg)
    except KeyboardInterrupt:
        logger.info("Atualizador de RUL interrompido.")
    finally:
        consumer.close()

if __name__ == "__main__":
    run_rul_updater()