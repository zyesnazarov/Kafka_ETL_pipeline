# 📊 Real-Time Cryptocurrency Data Pipeline

This project implements a **real-time cryptocurrency data pipeline** using **Kafka, InfluxDB, and PostgreSQL**. The pipeline:
✅ **Fetches real-time crypto market data from Binance** using `ccxt`.
✅ **Streams the data to Kafka** via a producer.
✅ **Processes and stores data** in **InfluxDB** (for Grafana visualization) and **PostgreSQL** (for historical analysis).

---

## 🛠️ Setup Instructions

### 1️⃣ **Prerequisites**
Before running the project, ensure you have the following installed:
- [Kafka](https://kafka.apache.org/)
- [InfluxDB 2.x](https://www.influxdata.com/)
- [PostgreSQL](https://www.postgresql.org/)
- Python 3.x with dependencies:
  ```sh
  pip install kafka-python influxdb-client ccxt psycopg2 pandas numpy json
  ```

### 2️⃣ **Start Kafka**
If Kafka is installed, start the server:
```sh
zookeeper-server-start.sh config/zookeeper.properties &
kafka-server-start.sh config/server.properties &
```
Create a Kafka topic:
```sh
kafka-topics.sh --create --topic my-first-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 3️⃣ **Start InfluxDB**
```sh
influxd
```
Create an InfluxDB bucket named `crypto-data` in the UI (`http://localhost:8086`).

### 4️⃣ **Start PostgreSQL**
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

## 🚀 Running the Pipeline

### **1️⃣ Start the Kafka Producer**
Run the producer script to stream real-time crypto data:
```sh
python producer-script.py
```
This script:
- Fetches **BTC/USDT** and **ETH/USDT** price data from Binance.
- Structures and sends data to Kafka every **5 seconds**.

### **2️⃣ Start the Kafka Consumer**
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

## 📈 Visualizing Data in Grafana
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

---

## 🔧 Troubleshooting
| Issue | Solution |
|--------|----------|
| Kafka consumer not receiving data | Check if Kafka is running (`kafka-console-consumer.sh` to test). |
| InfluxDB not storing data | Verify bucket name and API token in `consumer-script.py`. |
| Grafana not showing data | Check InfluxDB query range and ensure data is flowing. |
| PostgreSQL not storing data | Ensure table exists and matches schema. |

---

## ✨ Future Enhancements
🔹 **Add More KPIs**: RSI, Bollinger Bands, Moving Averages.  
🔹 **Optimize Kafka Performance**: Use multiple consumers for parallel processing.  
🔹 **Add Real-Time Alerts**: Trigger alerts if price_change_pct exceeds a threshold.

---

### 📜 License
This project is licensed under the MIT License.

---

### 🏆 Contributors
- **Your Name** - Initial Development

