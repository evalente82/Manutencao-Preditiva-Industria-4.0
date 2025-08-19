from pydantic import BaseModel

class TurbofanData(BaseModel):
    """
    Modelo de dados para uma leitura da turbina, baseado no dataset da NASA.
    """
    unit_number: int
    time_in_cycles: int
    
    op_setting_1: float
    op_setting_2: float
    op_setting_3: float
    
    sensor_1: float
    sensor_2: float
    sensor_3: float
    sensor_4: float
    sensor_5: float
    sensor_6: float
    sensor_7: float
    sensor_8: float
    sensor_9: float
    sensor_10: float
    sensor_11: float
    sensor_12: float
    sensor_13: float
    sensor_14: float
    sensor_15: float
    sensor_16: float
    sensor_17: float
    sensor_18: float
    sensor_19: float
    sensor_20: float
    sensor_21: float
