# app/main.py
from fastapi import FastAPI, HTTPException
from app.models import TurbofanData
from app import kafka_producer  # Importamos o módulo inteiro
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Serviço de Ingestão de Dados",
    description="API para receber dados de sensores e enviá-los para o Kafka.",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """Inicializa o producer do Kafka quando a aplicação inicia."""
    logger.info("Iniciando aplicação e criando producer do Kafka...")
    kafka_producer.producer = kafka_producer.get_kafka_producer()

@app.on_event("shutdown")
def shutdown_event():
    """Fecha o producer do Kafka de forma limpa quando a aplicação desliga."""
    logger.info("Desligando aplicação e fechando producer do Kafka...")
    kafka_producer.close_kafka_producer()

@app.get("/")
def read_root():
    return {"status": "Serviço de Ingestão de Dados está no ar!"}

@app.post("/ingest", status_code=202)
def ingest_data(data: TurbofanData):
    """Recebe dados de um sensor e os envia para o pipeline de processamento."""
    try:
        logger.info(f"Recebendo dados do motor: {data.unit_number}, ciclo: {data.time_in_cycles}")
        # Agora usamos a função send_to_kafka do módulo importado
        kafka_producer.send_to_kafka(data)
        return {"message": "Dados recebidos e enviados para processamento."}
    except Exception as e:
        logger.error(f"Erro no endpoint /ingest: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a requisição.")