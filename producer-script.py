# Importing necessary libraries
import pandas as pd
import ccxt
import time
from kafka import KafkaProducer
import json
from json import dumps


#initialize Kafka Producer
producer = KafkaProducer(bootstrap_servers = '3.95.137.41:9092',
                         value_serializer = lambda x:json.dumps(x).encode('utf-8')
)

# In the project I used binance as a source for real time information for cryptocurrencies
exchange = ccxt.binance()

# For the simplicity of the code, I choose BTC/USDT as a main CC for the code, list can be extended futher
symbols = ['BTC/USDT','ETH/USDT']

def round_value(value):
      if isinstance(value,(float,int)):
            return round(value,2)
      return value

while True:
        # fetching necessary details for our KPIs from ticker's dictionary
        for symbol in symbols:
            ticker = exchange.fetch_ticker(symbol)
            order_book = exchange.fetch_order_book(symbol, limit = 5)
            bid = order_book['bids'][0][0] if order_book['bids'] else None
            ask = order_book['asks'][0][0] if order_book['asks'] else None
            bid_volume = sum([x[1] for x in order_book['bids'][:5]]) if order_book['bids'] else None
            ask_volume = sum([x[1] for x in order_book['asks'][:5]]) if order_book['asks'] else None


            #structure the data

            crypto_data = {
                        "symbol": symbol,
                        "timestamp": ticker['timestamp'],
                        "open": round_value(ticker['open']),
                        "high": round_value(ticker['high']),
                        "low": round_value(ticker['low']),
                        "close": round_value(ticker['last']),
                        "volume": round_value(ticker['quoteVolume']),
                        "bid": round_value(bid),
                        "ask": round_value(ask),
                        "bid_volume": round_value(bid_volume),
                        "ask_volume": round_value(ask_volume),
                        "base_volume": round_value(ticker['baseVolume']),
                        "quote_volume": round_value(ticker['quoteVolume']),
                        "total_volume": round_value(ticker['baseVolume'] + ticker['quoteVolume'])
                    }
            producer.send('my-first-topic',value=crypto_data)
            time.sleep(5)

            print('')