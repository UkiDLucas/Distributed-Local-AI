""" agent_pong.py
A FastAPI-based AIKO agent that registers as 'PONG', waits for messages,
and responds to 'PING' with incremented replies.
"""

import time
import asyncio
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from common.zeroconf_utils import register_service
from common.config import settings

# --- Load configuration ---
AGENT_NAME = settings.AGENT_NAME
AGENT_PORT = settings.AGENT_PORT
MAX_COUNT = settings.MAX_COUNT
LOG_FILE = settings.LOG_FILE

# --- Setup logging ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format=f"%(asctime)s [{AGENT_NAME}] %(message)s"
)

# FastAPI app instance
app = FastAPI()

# --- Define message schema ---
class Message(BaseModel):
    message: str

# --- Core logic exposed for programmatic access ---
def run_action(message: str, user: dict) -> tuple[str, list[str]]:
    """
    Processes the incoming message and returns a reply for the PING agent.
    """
    count = int(message.split("#")[1])

    if count >= MAX_COUNT:
        return ("done", [])

    next_msg = f"message #{count + 1}"
    asyncio.create_task(log_reply(next_msg))
    return (f"Responded with: {next_msg}", [])

# --- Asynchronous logging of reply ---
async def log_reply(msg: str):
    await asyncio.sleep(0.01)
    logging.info(f"[{AGENT_NAME}] Replied with: {msg} at {time.time()}")

# --- Handle incoming message via HTTP ---
@app.post("/handle")
async def handle_message(msg: Message):
    """
    Handles messages received from PING. Returns an incremented reply
    up to MAX_COUNT.
    """
    logging.info(f"[{AGENT_NAME}] Received: {msg.message} at {time.time()}")
    context_md, matched_files = run_action(msg.message, user={})
    return {"context_md": context_md, "matched_files": matched_files}

# --- Startup event handler ---
@app.on_event("startup")
async def startup():
    """
    On startup, register this agent using Async Zeroconf so it can be
    discovered by the initiating PING agent.
    """
    await register_service(agent_name=AGENT_NAME, port=AGENT_PORT)
