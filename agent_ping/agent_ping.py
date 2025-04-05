""" agent_ping.py
A FastAPI-based AIKO agent that discovers 'PONG' via Zeroconf and sends
1000 ping-pong messages.
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

# --- Setup logging ---
logging.basicConfig(
    filename="console.txt",
    level=logging.INFO,
    format=f"%(asctime)s [{AGENT_NAME}] %(message)s"
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
    In this agent, the function drives a ping by forwarding a message.
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
    """
    Handles incoming messages. Responds to the sender by incrementing
    the message count and forwarding it. Ends when MAX_COUNT is reached.
    """
    logging.info(f"[{AGENT_NAME}] Received: {msg.message} at {time.time()}")
    context_md, matched_files = run_action(msg.message, user={})
    return {"context_md": context_md, "matched_files": matched_files}

# --- Startup event handler ---
@app.on_event("startup")
async def startup():
    """
    On startup, register this agent using Zeroconf and discover the
    target PONG agent. Once found, initiate the ping-pong sequence by
    sending the first message. This makes PING the initiator.
    """
    register_service(agent_name=AGENT_NAME, port=AGENT_PORT)
    global TARGET_URL
    TARGET_URL = await discover_target(TARGET_AGENT_NAME)

    if TARGET_URL:
        await asyncio.sleep(1)  # Give PONG a moment to be ready
        print(f"[{AGENT_NAME}] Starting message #0")
        await forward_message("message #0")
