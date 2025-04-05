""" agent_ping.py
Updated FastAPI AIKO agent that discovers 'PONG' via Zeroconf with retries.
"""

import time
import asyncio
import logging
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from common.zeroconf_utils import register_service, discover_target
from common.config import settings

# --- Load configuration ---
AGENT_NAME = settings.AGENT_NAME
AGENT_PORT = settings.AGENT_PORT
TARGET_AGENT_NAME = settings.TARGET_AGENT_NAME
MAX_COUNT = settings.MAX_COUNT
LOG_FILE = settings.LOG_FILE
DISCOVERY_RETRY_INTERVAL = 2  # seconds
DISCOVERY_MAX_RETRIES = 5

# --- Setup logging ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)s] [{AGENT_NAME}] %(message)s"
)

# FastAPI app instance
app = FastAPI()

# Store the discovered target agent URL
TARGET_URL = None

# --- Define message schema ---
class Message(BaseModel):
    message: str

# --- Core logic exposed for programmatic access ---
def run_action(message: str, user: dict) -> tuple[str, list[str]]:
    """
    Processes the user's message and returns (context_md, matched_files).
    This drives a ping by forwarding messages.
    """
    global TARGET_URL
    count = int(message.split("#")[1])

    if count >= MAX_COUNT:
        return ("done", [])

    next_msg = f"message #{count + 1}"
    asyncio.create_task(forward_message(next_msg))
    return (f"Sent: {next_msg}", [])

# --- Forward message to target asynchronously ---
async def forward_message(msg: str):
    await asyncio.sleep(0.01)
    if TARGET_URL:
        async with httpx.AsyncClient() as client:
            await client.post(TARGET_URL, json={"message": msg})
        logging.info(f"[{AGENT_NAME}] Sent: {msg} at {time.time()}")

# --- Handle incoming message via HTTP ---
@app.post("/handle")
async def handle_message(msg: Message):
    logging.info(f"[{AGENT_NAME}] Received: {msg.message}")
    run_action(msg.message, {})

# --- Startup logic to discover target with retries ---
@app.on_event("startup")
async def startup_event():
    global TARGET_URL

    await register_service(AGENT_NAME, AGENT_PORT)

    retries = 0
    while retries < DISCOVERY_MAX_RETRIES and not TARGET_URL:
        TARGET_URL = await discover_target(TARGET_AGENT_NAME)
        if not TARGET_URL:
            logging.warning(f"[{AGENT_NAME}] Could not discover {TARGET_AGENT_NAME}. Retrying...")
            await asyncio.sleep(DISCOVERY_RETRY_INTERVAL)
            retries += 1

    if TARGET_URL:
        logging.info(f"[{AGENT_NAME}] Discovered {TARGET_AGENT_NAME} at {TARGET_URL}")
        # Start the first message
        asyncio.create_task(forward_message("message #1"))
    else:
        logging.error(f"[{AGENT_NAME}] Failed to discover {TARGET_AGENT_NAME} after {DISCOVERY_MAX_RETRIES} retries.")
