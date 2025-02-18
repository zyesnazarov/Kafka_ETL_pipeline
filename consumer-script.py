import pandas as pd
from kafka import KafkaProducer, KafkaConsumer
import json
from json import dumps
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import psycopg2
import numpy as np
from datetime import datetime, timezone

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "TBD"
INFLUX_ORG = "personal"
INFLUX_BUCKET = "crypto-data"

#Initialize InfluxDB Client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

#Initializign a connection to Postsgresql
conn = psycopg2.connect("dbname=postgres user=postgres password=TBD host=localhost")
cursor = conn.cursor()

def compute_kpis(df):
    df = df.copy()
   # KPI specified as part of a request from the team
    df['price_change_pct'] = ((df['close'] - df['open']) / df['open']) * 100
    df['price_spread'] = df['ask'] - df['bid']
    df['daily_range'] = df['high'] - df['low']
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

    df['market_depth_ratio'] = (df['bid_volume'] + df['ask_volume']) / df['base_volume']
    df['order_book_imbalance'] = (df['bid_volume'] - df['ask_volume']) / df['total_volume']
    df['turnover_ratio'] = df['quote_volume'] / df['base_volume']

    # For the purposes of further ingestion in Postgresql, so that Python datatype remains and None for a compatibility
    df = df.astype(object)  
    df = df.where(pd.notnull(df), None) 

    return df.iloc[-1]  

def store_in_postgres(symbol, timestamp, kpis):

    timestamp = datetime.fromtimestamp(timestamp / 1000, timezone.utc)  

    sql = """
    INSERT INTO crypto_prices 
    (symbol, timestamp, price_change_pct, price_spread, daily_range, vwap, market_depth_ratio, order_book_imbalance, turnover_ratio)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        symbol, timestamp, kpis["price_change_pct"], kpis["price_spread"], kpis["daily_range"], kpis["vwap"], kpis["market_depth_ratio"], kpis["order_book_imbalance"], kpis["turnover_ratio"]
    )
    cursor.execute(sql, values)
    conn.commit()

consumer = KafkaConsumer(
    'my-first-topic',
    bootstrap_servers='3.95.137.41:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    session_timeout_ms=60000,  # Increase timeout to prevent disconnects
)

# Print available topics
print("Available topics:", consumer.topics())

for message in consumer:
    data = message.value
    df = pd.DataFrame([data])
    symbol, timestamp = data['symbol'], data['timestamp']
    latest_kpis = compute_kpis(df)
    store_in_postgres(symbol, timestamp, latest_kpis)

    point = Point("crypto_prices") \
        .tag("symbol", data["symbol"]) \
        .field("open", float(data["open"])) \
        .field("high", float(data["high"])) \
        .field("low", float(data["low"])) \
        .field("close", float(data["close"])) \
        .field("volume", float(data["volume"])) \
        .field("price_change_pct", float(latest_kpis["price_change_pct"])) \
        .field("price_spread", float(latest_kpis["price_spread"])) \
        .field("daily_range", float(latest_kpis["daily_range"])) \
        .field("vwap", float(latest_kpis["vwap"])) \
        .time(pd.to_datetime(data["timestamp"], unit='ms'))
    
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print(f"✅ Stored {symbol} data (with KPIs) in InfluxDB & PostgreSQL")
