# Real-Time Cryptocurrency Data Pipeline

This project was performed for a **Deloitte client** as part of a **Deloitte IT Advisory / Cloud Team project**. The client required **real-time cryptocurrency price tracking** along with **specified KPIs** and a **live visualization dashboard**.

I was responsible for writing the **business logic** for both the **Kafka producer and consumer scripts** based on the client's requirements. The client requested:&#x20;

- **Real-time price streaming**
- **Calculated KPIs (e.g., price change percentage, VWAP, MACD, etc.)**&#x20;
- **Live visualization of the data**

To meet these needs, I proposed a **data engineering solution** that:
✔ Utilized **Kafka for real-time data streaming**\
✔ Stored live data in **InfluxDB** for **real-time Grafana visualization**\
✔ Stored historical results in **PostgreSQL** for analytical processing

---

## 🛠️ Setup Instructions

### 1. Prerequisites

Before running the project, ensure you have the following installed:

- [Kafka](https://kafka.apache.org/)
- [InfluxDB 2.x](https://www.influxdata.com/)
- [PostgreSQL](https://www.postgresql.org/)
- Python 3.x with dependencies:
  ```sh
  pip install kafka-python influxdb-client ccxt psycopg2 pandas numpy json
  ```

### 2. Start Kafka

If Kafka is installed, start the server:

```sh
zookeeper-server-start.sh config/zookeeper.properties &
kafka-server-start.sh config/server.properties &
```

Create a Kafka topic:

```sh
kafka-topics.sh --create --topic my-first-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 3. Start InfluxDB

```sh
influxd
```

Create an InfluxDB bucket named `crypto-data` in the UI (`http://localhost:8086`).

### 4. Start PostgreSQL

Ensure PostgreSQL is running and create the required table:

```sql
CREATE TABLE crypto_prices (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    timestamp TIMESTAMP,
    price_change_pct FLOAT,
    price_spread FLOAT,
    daily_range FLOAT,
    vwap FLOAT,
    market_depth_ratio FLOAT,
    order_book_imbalance FLOAT,
    turnover_ratio FLOAT
);
```

---

## Running the Pipeline

### **1. Start the Kafka Producer**

Run the producer script to stream real-time crypto data:

```sh
python producer-script.py
```

This script:

- Fetches **BTC/USDT** and **ETH/USDT (as en example)** price data from Binance.
- Structures and sends data to Kafka every **5 seconds** **(can be further adjusted)**

### **2. Start the Kafka Consumer**

Run the consumer script to store data:

```sh
python consumer-script.py
```

This script:

- **Consumes messages from Kafka**.
- **Computes KPIs** (e.g., `price_change_pct`, `VWAP`, `MACD`).
- **Stores data in InfluxDB** for **Grafana visualization**.
- **Stores data in PostgreSQL** for **historical analysis**.

---

## 3. Visualizing Data in Grafana

1. **Go to Grafana UI** (`http://localhost:3000`).
2. **Add InfluxDB as a Data Source**:
   - URL: `http://localhost:8086`
   - Database: `crypto-data`
   - Authentication: Use **InfluxDB API Token**
3. **Create a New Dashboard** → Add a Panel.
4. **Use this Flux Query to visualize price data**:
   ```flux
   from(bucket: "crypto-data")
   |> range(start: -6h)
   |> filter(fn: (r) => r._measurement == "crypto_prices")
   |> filter(fn: (r) => r.symbol == "BTC/USDT")
   |> filter(fn: (r) => r._field == "price_change_pct" or r._field == "open" or r._field == "low" or r._field == "high" or r._field == "close")
   |> yield()
   ```
5. **Set visualization to "Time Series"** and adjust axes.
6. **Click "Save & Apply" to view live crypto price trends!**



