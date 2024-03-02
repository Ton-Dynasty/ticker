from ticton import TicTonAsyncClient
from dotenv import load_dotenv
import redis.asyncio as redis
import asyncio
import os
import json
from price import set_price, get_exchanges
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytoncenter.v3.models import WaitMessageExistsRequest, GetTransactionTraceRequest
from pytoncenter.address import Address
from helper import wait_ring_success, wait_tick_success
from threading import Thread
import logging
from logging.handlers import RotatingFileHandler
from decimal import Decimal

PRICE_OUTDATED_TRHESSHOLD = 3  # if price is outdated for 3 seconds, we need to wait for the next update
WAIT_SECONDS_IF_PRICE_OUTDATED = 10  # Wait for 10 seconds if the price is outdated
HEARTBEAT_INTERVAL = 180  # run tick every 3 minutes
WAIT_SECONDS_TO_CLOSE_POSITION = 120  # close the position after 2 minutes
TON_BALANCE_THRESHOLD = Decimal("2000000000")  # 2 TON

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
LOGGER.addHandler(stream_handler)
log_file_handler = RotatingFileHandler("price.log", maxBytes=10 * 1024 * 1024, backupCount=5)  # 10 MB
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
log_file_handler.setFormatter(formatter)
LOGGER.addHandler(log_file_handler)

load_dotenv(dotenv_path=".env", override=True, verbose=True)

scheduler = AsyncIOScheduler()

redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD"),
)


async def auto_close_position(client: TicTonAsyncClient, boc: str):
    try:
        alarm_id = await wait_tick_success(client.toncenter, boc)
        await asyncio.sleep(WAIT_SECONDS_TO_CLOSE_POSITION)  # Wait for 70 seconds, and then close the position
        sent = await client.ring(alarm_id)
        await wait_ring_success(client.toncenter, sent.message_hash)
    except Exception as e:
        LOGGER.error(f"Error: {e}")
        return


async def main():
    # Start scheduler
    scheduler.add_job(set_price, "interval", seconds=3, args=[get_exchanges(), redis_client])
    scheduler.start()

    # Start hearbeat
    client = await TicTonAsyncClient.init(logger=LOGGER)
    while True:
        # Check user balance
        ton_balance, _ = await client._get_user_balance(owner_address=client.wallet.address.to_string(True))
        if ton_balance < TON_BALANCE_THRESHOLD:
            LOGGER.warning(f"TON balance is low: {ton_balance}")
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            continue
        raw = await redis_client.get("ticker:price")
        if raw is None:
            LOGGER.error("Price is not available")
            await asyncio.sleep(WAIT_SECONDS_IF_PRICE_OUTDATED)
            continue

        response = json.loads(raw)
        timestanp = response["timestamp"]
        price = response["price"]

        # If the price is outdated, we need to wait for the next update
        now = datetime.now().timestamp()
        if now - timestanp > PRICE_OUTDATED_TRHESSHOLD:
            LOGGER.warning(f"Price is outdated: {now - timestanp} seconds")
            await asyncio.sleep(WAIT_SECONDS_IF_PRICE_OUTDATED)
            continue

        # Send the price to the blockchain
        sent = await client.tick(price=price)
        t = Thread(target=asyncio.run, args=(auto_close_position(client, sent.message_hash),))
        t.start()
        await asyncio.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
