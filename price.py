from typing import List, Tuple, Optional
import ccxt.async_support as ccxt
import redis.asyncio as redis
from ccxt import Exchange
import asyncio
import datetime
import json
import logging
from logging.handlers import RotatingFileHandler

# Create a logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
LOGGER.addHandler(stream_handler)
log_file_handler = RotatingFileHandler("price.log", maxBytes=10 * 1024 * 1024, backupCount=5)  # 10 MB
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
log_file_handler.setFormatter(formatter)
LOGGER.addHandler(log_file_handler)


def get_exchanges() -> List[Exchange]:
    options = ["bybit", "gateio", "okx"]
    return [getattr(ccxt, opt)() for opt in options]


async def fetch_price(exchange: Exchange, symbol: str, **kwargs) -> Tuple[Optional[str], str, Optional[float]]:
    ticker = await exchange.fetch_ticker(symbol)
    return exchange.name, symbol, ticker.get("last", None)


async def set_price(exchanges: List[Exchange], redis_client: redis.StrictRedis):
    assert len(exchanges) > 0, "exchange list cannot be empty"
    jobs = []
    for exchange in exchanges:
        jobs.append(fetch_price(exchange, "TON/USDT"))
    results: List[Tuple[Optional[str], str, float]] = await asyncio.gather(*jobs)
    candidates = []
    for _, _, price in results:
        if price is not None:
            candidates.append(price)
    average = sum(candidates) / len(candidates)
    timestamp = datetime.datetime.now().timestamp()
    await redis_client.set("ticker:price", json.dumps({"price": average, "timestamp": timestamp}))
