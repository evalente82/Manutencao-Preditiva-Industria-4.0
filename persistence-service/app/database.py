import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Variável de ambiente DATABASE_URL não definida!")

# O engine é o ponto de entrada para o banco de dados
engine = create_engine(DATABASE_URL)

# SessionLocal é uma fábrica de sessões. Cada instância será uma sessão com o banco.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base será usada como classe base para nossos modelos de tabela
Base = declarative_base()