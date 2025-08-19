from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models

def get_latest_engine_data(db: Session, skip: int = 0, limit: int = 100):
    """
    Busca os últimos 'limit' registros de dados de motores, ordenados pelo ciclo mais recente.
    """
    return db.query(models.EngineData).order_by(models.EngineData.created_at.desc()).offset(skip).limit(limit).all()

def get_engine_data_by_unit(db: Session, unit_number: int, skip: int = 0, limit: int = 1000):
    """
    Busca todos os registros de um motor específico (unit_number), ordenados pelo ciclo.
    """
    return db.query(models.EngineData).filter(models.EngineData.unit_number == unit_number).order_by(models.EngineData.time_in_cycles.asc()).offset(skip).limit(limit).all()


def get_latest_data_for_all_units(db: Session, limit_per_unit: int = 200):
    """
    Busca os últimos 'limit_per_unit' registros para cada motor usando Window Functions.
    É uma forma eficiente de fazer a query "N per group".
    """
    # Esta query usa uma função de janela (ROW_NUMBER) para numerar os registros
    # de cada motor em ordem decrescente de ciclo, e então pega apenas os que
    # têm uma numeração menor ou igual ao limite.
    query = text(f"""
        SELECT id, created_at, unit_number, time_in_cycles, op_setting_1, op_setting_2, 
               op_setting_3, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_6, 
               sensor_7, sensor_8, sensor_9, sensor_10, sensor_11, sensor_12, sensor_13, 
               sensor_14, sensor_15, sensor_16, sensor_17, sensor_18, sensor_19, 
               sensor_20, sensor_21, rul
        FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY unit_number ORDER BY time_in_cycles DESC) as rn
            FROM engine_data
        ) as sub
        WHERE sub.rn <= {limit_per_unit}
        ORDER BY sub.unit_number, sub.time_in_cycles ASC;
    """)
    
    result = db.execute(query)
    # Mapeia o resultado bruto para o modelo SQLAlchemy
    return [models.EngineData(**row) for row in result.mappings()]