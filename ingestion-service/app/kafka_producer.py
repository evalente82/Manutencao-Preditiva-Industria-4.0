# app/kafka_producer.py
import os
import json
from confluent_kafka import Producer
from dotenv import load_dotenv
from app.models import TurbofanData

load_dotenv()

KAFKA_TOPIC = "sensor-data"

# Variável para armazenar a instância do producer
producer: Producer = None

def get_kafka_producer() -> Producer:
    """Cria e retorna uma instância do Producer do Kafka."""
    kafka_config = {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': os.getenv('KAFKA_API_KEY'),
        'sasl.password': os.getenv('KAFKA_API_SECRET'),
        # Adicionar um client.id pode ajudar na identificação no broker
        'client.id': 'ingestion-service-producer' 
    }
    return Producer(kafka_config)

def delivery_report(err, msg):
    """Callback executado quando uma mensagem é entregue ou falha."""
    if err is not None:
        print(f"Falha ao entregar mensagem: {err}")
    else:
        print(f"Mensagem entregue ao tópico {msg.topic()} [{msg.partition()}]")

def send_to_kafka(data: TurbofanData):
    """Envia os dados do sensor para o tópico Kafka de forma assíncrona."""
    global producer
    if not producer:
        print("Erro: Producer do Kafka não foi inicializado.")
        return

    try:
        json_payload = data.model_dump_json()
        producer.produce(
            KAFKA_TOPIC,
            key=str(data.unit_number),
            value=json_payload.encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)
    except Exception as e:
        print(f"Erro ao enviar para o Kafka: {e}")

def close_kafka_producer():
    """Garante que todas as mensagens pendentes sejam enviadas antes de fechar."""
    global producer
    if producer:
        print("Encerrando o producer do Kafka e enviando mensagens restantes...")
        producer.flush()