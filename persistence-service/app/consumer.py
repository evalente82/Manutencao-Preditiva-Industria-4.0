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

KAFKA_TOPIC = "sensor-data"

kafka_config = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_API_KEY'),
    'sasl.password': os.getenv('KAFKA_API_SECRET'),
    'group.id': 'persistence-group-raw-data-1', # Novo grupo para dados brutos
    'auto.offset.reset': 'earliest'
}

def process_message(msg):
    try:
        data = json.loads(msg.value().decode('utf-8'))
        logger.info(f"Mensagem recebida do motor: {data.get('unit_number')}")

        db = SessionLocal()
        try:
            # O Pydantic model e o SQLAlchemy model têm os mesmos nomes de campo,
            # então podemos desempacotar o dicionário diretamente.
            db_reading = EngineData(**data)
            db.add(db_reading)
            db.commit()
            logger.info(f"Dados do motor {data.get('unit_number')} salvos no banco.")
        finally:
            db.close()

    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar JSON: {msg.value()}")
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")

def run_consumer():
    consumer = Consumer(kafka_config)
    consumer.subscribe([KAFKA_TOPIC])
    logger.info(f"Consumidor Kafka iniciado no tópico '{KAFKA_TOPIC}'. Aguardando mensagens...")

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
        logger.info("Consumidor interrompido.")
    finally:
        consumer.close()

if __name__ == "__main__":
    run_consumer()
