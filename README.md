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

## Documentação do Projeto: Dashboard de Manutenção Preditiva

Este documento descreve o processo de treinamento do modelo de Machine Learning e a interpretação dos dados exibidos no dashboard interativo.

### Seção 1: O Processo de Treinamento do Modelo LSTM

O "cérebro" da aplicação é um modelo de Deep Learning do tipo LSTM (Long Short-Term Memory), que foi treinado para prever a Vida Útil Remanescente (RUL) de motores de turbina de avião. O treinamento seguiu um fluxo de trabalho padrão de Machine Learning, dividido nas seguintes etapas:

1. **Preparação dos Dados:**
   - **Fonte:** Foi utilizado o renomado dataset "Turbofan Engine Degradation Simulation" da NASA, especificamente o arquivo train_FD001.txt. Este arquivo contém o histórico completo de dados de 100 motores, desde o início de sua operação até a falha.
   - **Conteúdo:** Cada linha do arquivo representa um ciclo de voo e contém 21 leituras de sensores, 3 configurações operacionais, o número do motor e o ciclo atual.

2. **Engenharia de Features (Cálculo da RUL):**
   - O passo mais crucial foi criar a nossa "variável alvo" — aquilo que queríamos que o modelo aprendesse a prever. Calculamos a Vida Útil Remanescente (RUL) para cada ciclo de cada motor.
   - **Lógica:** Para um motor que falhou, por exemplo, no ciclo 192, seu RUL no ciclo 1 era 191, no ciclo 2 era 190, e assim por diante.
   - **Ajuste Fino (Clipping):** A RUL foi "achatada" ou limitada a um valor máximo de 125. Isso foi feito para que o modelo focasse em aprender os padrões de degradação que ocorrem mais perto da falha, em vez de tentar prever com exatidão a vida útil de um motor praticamente novo.

3. **Normalização dos Dados (Escalonamento):**
   - Redes Neurais como LSTMs são sensíveis à escala dos dados de entrada. Sensores com valores muito grandes (ex: pressão) podem ofuscar sensores com valores pequenos.
   - Para resolver isso, utilizamos um MinMaxScaler do Scikit-learn para transformar todos os 24 valores de entrada (sensores e configurações) para uma escala comum entre 0 e 1.
   - **Artefato Gerado:** O escalonador treinado foi salvo no arquivo scaler.pkl, para que pudéssemos aplicar a mesma exata transformação aos novos dados na fase de predição.

4. **Criação de Sequências Temporais:**
   - Um modelo LSTM não olha para um único momento no tempo; ele aprende com sequências. Transformamos os dados em "janelas de tempo".
   - Para cada ponto, o modelo recebia como entrada (X) os dados dos últimos 50 ciclos de voo e era treinado para prever (Y) a RUL do ciclo seguinte.
   - Isso permite que o modelo aprenda não apenas os valores dos sensores, mas também suas tendências e a evolução do desgaste ao longo do tempo.

5. **Construção e Treinamento do Modelo:**
   - Foi construído um modelo de Deep Learning usando TensorFlow/Keras. A arquitetura consistia em camadas LSTM empilhadas, ideais para dados sequenciais, e camadas de Dropout para evitar que o modelo "decorasse" os dados de treino.
   - O modelo foi treinado com as sequências geradas, aprendendo a associar os padrões de desgaste dos sensores com a RUL correspondente.
   - **Artefato Gerado:** O modelo treinado foi salvo no arquivo rul_prediction_model.h5.

### Seção 2: O Que o Dashboard Demonstra

O dashboard é a materialização de toda a pipeline de MLOps, demonstrando como um modelo treinado pode ser usado "em produção" para analisar dados em tempo real.

1. **O Fluxo de Dados em Tempo Real:**
   - O "Log da Simulação" mostra o "pulso" do sistema. Cada linha representa um novo pacote de dados de sensor sendo gerado pelo simulador_continuo.py e enviado para a pipeline, simulando um motor real em operação.
   - Esses dados passam pelo ingestion-service, são publicados no Kafka e consumidos simultaneamente pelos serviços de persistência e predição.

2. **A Interpretação dos Gráficos:**
   - **Gráficos de Histórico dos Sensores:**
     - Estes gráficos (sensor_2, sensor_3, etc.) mostram uma seleção dos dados de entrada que o modelo de IA está recebendo.
     - Eles permitem observar visualmente as tendências de cada sensor. Você pode notar que alguns sensores têm uma tendência clara de subida ou descida à medida que o motor se aproxima do fim da vida, indicando desgaste.
   
   - **Gráfico de Vida Útil Remanescente (RUL):**
     - Este é o gráfico principal e mostra o resultado da predição do modelo.
     - **Eixo X (Tempo em Ciclos):** Mostra a "idade" do motor em número de voos completados.
     - **Eixo Y (RUL):** Mostra a previsão do modelo de quantos voos ainda restam para aquele motor.
     - **A História:** A tendência de queda da linha da RUL é a demonstração visual do sucesso do modelo. Ele está identificando corretamente que, à medida que o motor é mais usado (ciclos aumentam), sua vida útil restante diminui. As flutuações no gráfico (como as vistas no Motor #1) demonstram a sensibilidade do modelo às variações aleatórias nos dados dos sensores simulados.

## Como Executar

# Projeto de Manutenção Preditiva para Indústria 4.0

![Dashboard Preview](https://via.placeholder.com/800x400.png?text=Dashboard+Preview)
![Architecture Diagram](https://via.placeholder.com/800x400.png?text=Architecture+Diagram)
![Kafka Setup](https://via.placeholder.com/800x400.png?text=Kafka+Setup)
![Simulation Demo](https://via.placeholder.com/800x400.png?text=Simulation+Demo)

Este projeto é um sistema completo de manutenção preditiva construído com uma arquitetura de microserviços e Apache Kafka. O sistema simula a coleta de dados de sensores em tempo real, processa através de uma pipeline de eventos, utiliza um modelo de Deep Learning (LSTM) para prever a Vida Útil Remanescente (RUL) de turbinas de avião e exibe os resultados em um dashboard interativo que se atualiza automaticamente.

## 📋 Sumário
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Documentação do Modelo LSTM](#documentação-do-modelo-lstm)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Execução do Sistema](#execução-do-sistema)
- [Visualização do Dashboard](#visualização-do-dashboard)

## Arquitetura do Sistema

O fluxo de dados segue a seguinte arquitetura de microsserviços:

```
Simulador Contínuo → API de Ingestão → Kafka (Confluent) → Serviço de Predição (ML)
                                                       → Serviço de Persistência → Banco de Dados (PostgreSQL) → API do Dashboard (WebSockets) → Frontend (Navegador)
```

## Tecnologias Utilizadas

- **Backend:** Python (FastAPI)
- **Frontend:** React
- **Mensageria:** Apache Kafka (Confluent Cloud)
- **Banco de Dados:** PostgreSQL
- **Machine Learning:** TensorFlow/Keras (LSTM)
- **Containerização:** Docker (opcional)

## Documentação do Modelo LSTM

### O Processo de Treinamento do Modelo LSTM

O "cérebro" da aplicação é um modelo de Deep Learning do tipo LSTM (Long Short-Term Memory), treinado para prever a Vida Útil Remanescente (RUL) de motores de turbina de avião.

#### 1. Preparação dos Dados
- **Fonte:** Dataset "Turbofan Engine Degradation Simulation" da NASA (train_FD001.txt)
- **Conteúdo:** Histórico completo de 100 motores, com 21 leituras de sensores, 3 configurações operacionais, número do motor e ciclo atual por linha

#### 2. Engenharia de Features (Cálculo da RUL)
- Criada a variável alvo Vida Útil Remanescente (RUL)
- **Lógica:** Para um motor que falhou no ciclo 192, seu RUL no ciclo 1 era 191, no ciclo 2 era 190, etc.
- **Ajuste Fino (Clipping):** RUL limitada a valor máximo de 125 para focar nos padrões de degradação próximos à falha

#### 3. Normalização dos Dados (Escalonamento)
- Utilizado MinMaxScaler do Scikit-learn para escala 0-1
- **Artefato Gerado:** scaler.pkl (para aplicar mesma transformação em novos dados)

#### 4. Criação de Sequências Temporais
- Transformação dos dados em "janelas de tempo"
- Modelo recebe dados dos últimos 50 ciclos para prever RUL do ciclo seguinte

#### 5. Construção e Treinamento do Modelo
- Arquitetura com camadas LSTM empilhadas e camadas Dropout
- **Artefato Gerado:** rul_prediction_model.h5

### O Que o Dashboard Demonstra

#### 1. Fluxo de Dados em Tempo Real
- "Log da Simulação" mostra dados sendo gerados e processados
- Dados passam pelo ingestion-service, Kafka e são consumidos por persistência e predição

#### 2. Interpretação dos Gráficos
- **Gráficos de Histórico dos Sensores:** Mostram tendências de desgaste
- **Gráfico de Vida Útil Remanescente (RUL):**
  - Eixo X: Tempo em Ciclos (idade do motor)
  - Eixo Y: RUL (previsão de voos restantes)
  - Tendência de queda demonstra sucesso do modelo

## Pré-requisitos

Antes de começar, garanta que você tenha:

1. **Git** instalado
2. **Python 3.11+** com gerenciador de pacotes `pip`
3. **Conta na Confluent Cloud** (plano gratuito suficiente):
   - Crie em [Confluent Cloud](https://www.confluent.io/confluent-cloud/)
   - Obtenha: `Bootstrap Server`, `API Key` e `API Secret`
4. **Banco de Dados PostgreSQL** (local ou em nuvem):
   - Serviços gratuitos recomendados: [Neon](https://neon.tech/), [Supabase](https://supabase.com/) ou [ElephantSQL](https://www.elephantsql.com/)
   - Obtenha a **URL de Conexão** (formato: `postgresql://user:password@host:port/dbname`)

## Instalação e Configuração

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/evalente82/Manutencao-Preditiva-Industria-4.0.git
cd Manutencao-Preditiva-Industria-4.0
```

### Passo 2: Configurar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows (PowerShell):
.\venv\Scripts\Activate
# No macOS/Linux:
source venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com:

```env
# Credenciais do Confluent Cloud
KAFKA_BOOTSTRAP_SERVERS="pkc-xxxx.us-east-2.aws.confluent.cloud:9092"
KAFKA_API_KEY="SUA_API_KEY"
KAFKA_API_SECRET="SEU_API_SECRET"

# URL de Conexão do PostgreSQL
DATABASE_URL="postgresql://user:password@host:port/dbname"
```

### Passo 5: Criar Tópicos no Kafka

No painel do Confluent Cloud:
1. Acesse **"Topics"**
2. Clique em **"Create topic"** e crie:
   - `sensor-data`
   - `prediction-results`
3. (Opcional) Configure `retention.ms` para limpeza automática

## Execução do Sistema

Para executar o sistema completo, abra **6 terminais separados**, navegue até a pasta do projeto e ative o ambiente virtual em cada um.

| Terminal | Comando | Porta/Função |
|----------|---------|--------------|
| 1. API de Ingestão | `uvicorn ingestion_service.app.main:app --reload --port 8000` | Porta 8000 |
| 2. API do Dashboard | `uvicorn dashboard_service.app.main:app --reload --port 8001` | Porta 8001 |
| 3. Serviço de Predição | `python prediction_service/app/service.py` | Processamento ML |
| 4. Persistência (Dados Brutos) | `python persistence_service/app/consumer.py` | Consume `sensor-data` |
| 5. Persistência (Atualizador RUL) | `python persistence_service/app/rul_updater.py` | Atualiza previsões |
| 6. Simulador Contínuo | `python simulador_continuo.py` | Gera dados de teste |

## Visualização do Dashboard

Com todos os 6 terminais em execução:

1. Abra seu navegador
2. Arraste o arquivo `dashboard-service/index.html` para a barra de endereços
3. Clique em **"INICIAR SIMULAÇÃO"** para ver os dados em tempo real

O dashboard exibirá:
- Log da simulação em tempo real
- Gráficos históricos dos sensores
- Gráfico de Vida Útil Remanescente (RUL) com previsões atualizadas
- Tendências de desgaste e alertas de manutenção