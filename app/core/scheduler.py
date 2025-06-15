from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.providers.yahoo import YahooFinanceProvider
from app.services.kafka.producer import publish_price_event
from datetime import datetime, timezone
import uuid
import traceback

scheduler = BackgroundScheduler(timezone="UTC")
if not scheduler.running:
    scheduler.start()
    print("🟢 APScheduler started?", scheduler.running)

def start_polling_job(symbols, interval, provider):
    print(f"📆 Registering polling job for {symbols} every {interval}s via {provider}")

    provider_instance = YahooFinanceProvider()

    def job():
        try:
            for symbol in symbols:
                print(f"Executing polling job for {symbol} at {datetime.now(timezone.utc)}")
                price = provider_instance.get_latest_price(symbol)
                publish_price_event({
                    "symbol": price.symbol,
                    "price": price.price,
                    "timestamp": price.timestamp,
                    "source": provider,
                    "raw_response_id": str(uuid.uuid4())
                })
                print(f"[{symbol}] Published price event at {datetime.now(timezone.utc)}")
        except Exception:
            print(f"Polling job crashed for symbols {symbols}")
            traceback.print_exc()

    job_id = f"{provider}-{'-'.join(symbols)}-{interval}"
    scheduler.add_job(job, IntervalTrigger(seconds=interval), id=job_id, replace_existing=True)

