# Projeto de Manutenção Preditiva para Indústria 4.0

Este projeto é um sistema de manutenção preditiva construído com uma arquitetura de microserviços e Apache Kafka. O objetivo é simular a coleta de dados de sensores, prever falhas em equipamentos e exibir os resultados em um dashboard em tempo real.

## Arquitetura

O sistema é composto pelos seguintes microserviços:
- **ingestion-service:** Recebe dados de sensores.
- **prediction-service:** Analisa os dados e executa modelos de ML.
- **persistence-service:** Armazena os dados em um banco de dados.
- **alerting-service:** Envia alertas sobre possíveis falhas.
- **dashboard-service:** Interface web para visualização.

## Tecnologias
- **Backend:** Python (FastAPI)
- **Frontend:** React
- **Mensageria:** Apache Kafka
- **Banco de Dados:** PostgreSQL
- **Containerização:** Docker

## Como Executar
(Instruções serão adicionadas conforme o desenvolvimento avança)
