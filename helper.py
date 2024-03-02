from pytoncenter import AsyncTonCenterClientV3
from pytoncenter.v3.models import *
from pytoncenter.address import Address
from pytoncenter.extension.message import JettonMessage
from tonpy import CellSlice
import logging
import asyncio
from logging.handlers import RotatingFileHandler

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
LOGGER.addHandler(stream_handler)

log_file_handler = RotatingFileHandler("helper.log", maxBytes=10 * 1024 * 1024, backupCount=5)  # 10 MB

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
log_file_handler.setFormatter(formatter)

LOGGER.addHandler(log_file_handler)


async def wait_tick_success(client: AsyncTonCenterClientV3, msg_hash: str):
    tx = await anext(client.wait_message_exists(WaitMessageExistsRequest(msg_hash=msg_hash)))
    trace = await client.get_trace_alternative(GetTransactionTraceRequest(hash=tx.hash))
    # Search transaction by opcode 0x09c0fafb
    branches = trace.children[0].children[0]
    for branch in branches.children:
        if branch.transaction.in_msg.opcode == JettonMessage.TransferNotification.OPCODE:
            target_tx = branch.children[0].transaction
            body = target_tx.in_msg.message_content.body
            cs = CellSlice(body)
            _ = cs.load_uint(32)
            alarm_id = cs.load_uint(256)
            LOGGER.info(f"Open an Alarm ID: {alarm_id}")
            return alarm_id
    raise Exception("Alarm ID not found")


async def wait_ring_success(client: AsyncTonCenterClientV3, msg_hash: str):
    tx = await anext(client.wait_message_exists(WaitMessageExistsRequest(msg_hash=msg_hash)))
    LOGGER.info(f"Ring complete, Transaction hash: {tx.hash}")
    return
