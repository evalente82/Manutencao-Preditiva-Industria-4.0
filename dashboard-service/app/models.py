from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

class EngineData(Base):
    """
    Modelo da tabela para armazenar os dados dos sensores da turbina,
    baseado no dataset da NASA.
    """
    __tablename__ = "engine_data"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    unit_number = Column(Integer, index=True, nullable=False)
    time_in_cycles = Column(Integer, nullable=False)
    
    op_setting_1 = Column(Float, nullable=False)
    op_setting_2 = Column(Float, nullable=False)
    op_setting_3 = Column(Float, nullable=False)
    
    sensor_1 = Column(Float, nullable=False)
    sensor_2 = Column(Float, nullable=False)
    sensor_3 = Column(Float, nullable=False)
    sensor_4 = Column(Float, nullable=False)
    sensor_5 = Column(Float, nullable=False)
    sensor_6 = Column(Float, nullable=False)
    sensor_7 = Column(Float, nullable=False)
    sensor_8 = Column(Float, nullable=False)
    sensor_9 = Column(Float, nullable=False)
    sensor_10 = Column(Float, nullable=False)
    sensor_11 = Column(Float, nullable=False)
    sensor_12 = Column(Float, nullable=False)
    sensor_13 = Column(Float, nullable=False)
    sensor_14 = Column(Float, nullable=False)
    sensor_15 = Column(Float, nullable=False)
    sensor_16 = Column(Float, nullable=False)
    sensor_17 = Column(Float, nullable=False)
    sensor_18 = Column(Float, nullable=False)
    sensor_19 = Column(Float, nullable=False)
    sensor_20 = Column(Float, nullable=False)
    sensor_21 = Column(Float, nullable=False)
    
    rul = Column(Integer, nullable=True)
