# This script consumes price events from Kafka and calculates the moving average for each symbol.
from confluent_kafka import Consumer, KafkaError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.price_point import PricePoint
from app.models.symbol_average import SymbolAverage
from datetime import datetime
import json
import time

# Wait for Kafka to be ready before starting the consumer
print("⏳ Waiting for Kafka to be ready...")
time.sleep(10)

conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'ma-consumer-group',
    'auto.offset.reset': 'latest'
}
print(f"{conf}")
consumer = Consumer(conf)
consumer.subscribe(['price-events'])

def calculate_moving_average(prices: list[float]) -> float:
    """Calculate the 5-point moving average for a list of prices."""
    return round(sum(prices[-5:]) / min(len(prices), 5), 2)

def process_message(event_data: dict, db: Session):
    """
    Process a price event, fetch recent prices, calculate the moving average,
    and update the SymbolAverage table in the database.
    """
    symbol = event_data["symbol"]
    timestamp = datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00"))

    # Get last 5 prices
    recent_prices = db.query(PricePoint.price).filter(
        PricePoint.symbol == symbol
    ).order_by(PricePoint.timestamp.desc()).limit(5).all()

    prices = [p[0] for p in reversed(recent_prices)]
    if not prices:
        return

    avg = calculate_moving_average(prices)


    db.merge(SymbolAverage(
        symbol=symbol,
        timestamp=timestamp,
        moving_average=avg
    ))
    db.commit()
    print(f"[{symbol}] Moving average stored: {avg} at {timestamp}")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"⚠️ Kafka message error: {msg.error()}")
        continue


    try:
        payload = json.loads(msg.value().decode('utf-8'))
        db = SessionLocal()
        process_message(payload, db)
        db.close()
    except Exception as e:
        print("Error processing message:", e)
