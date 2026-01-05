# Real-Time Market Streaming Pipeline (Kafka + PostgreSQL + Python)

## Requirements
- PostgreSQL installed and running
- Python 3 with pip and venv
- Kafka (not included in this repo due to GitHub file size limits)
- macOS or Linux terminal

---

## Project Structure
```
src/
├── 0dbInit/
│ └── dbInit.py
├── 1producers/
│ ├── binanceProducer.py
│ ├── fakeStockProducer.py
├── 2kafka/
│ └── versions.txt
├── 3consumers/
│ ├── AtiqueConsumer.py
│ ├── binanceConsumer.py
│ └── fakeStockConsumer.py
├── 4postgres/
│ └── tradeDBSample.sql
├── 6DashboardOrNotifier/
│ └── Dashboard.py
└── websockets/
└── sample.py
```

---

## Step 1 Start PostgreSQL
Make sure PostgreSQL is running.

Default connection used by consumers:
```
DB_NAME = trades
DB_USER = postgres
DB_PASS = ""
DB_HOST = localhost
DB_PORT = 5432
```

---

## Step 2 Initialize database tables
From the `src` folder:
```bash
cd src
python 0dbInit/dbInit.py
```

This creates:
- `trades`
- `asset_volatility`
- `alerts`

---

## Step 3 Download and start Kafka

Kafka is **NOT included** in this repo due to GitHub file size limits.  
You must download it manually.

### 1 Download Kafka
Go to:

https://kafka.apache.org/downloads

Download the **Binary**:
- `kafka_2.13-4.1.1.tgz`

### 2 Move it into the project
Place the file here: 
src/2kafka/kafka_2.13-4.1.1.tgz


### 3 Extract Kafka
```bash
cd src/2kafka
tar -xvf kafka_2.13-4.1.1.tgz
cd kafka_2.13-4.1.1
```

### 4 Start ZooKeeper (Terminal 1)
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

### 5 Start Kafka broker (Terminal 2)
```bash
bin/kafka-server-start.sh config/server.properties
```

---

## Step 4 Create Kafka topics
Open a new terminal and run:

```bash
cd src/2kafka/kafka_2.13-4.1.1

bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
  --topic fakestock --partitions 10 --replication-factor 1

bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
  --topic binance --partitions 10 --replication-factor 1
```

---

## Step 5 Start consumers
From `src`:

```bash
python 3consumers/AtiqueConsumer.py
python 3consumers/fakeStockConsumer.py
```

---

## Step 6 Start producers
In separate terminals:

```bash
python 1producers/binanceProducer.py
python 1producers/fakeStockProducer.py
```

---

## Step 7 Start dashboard
From `src`:

```bash
python 6DashboardOrNotifier/Dashboard.py
```

Dashboard runs on:
```
http://127.0.0.1:8050
```

---

## Pipeline summary
WebSocket to Kafka to Consumers to PostgreSQL to Dashboard
Alerts are generated using EWMA volatility baselines and stored in PostgreSQL
