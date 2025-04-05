""" agent_ping.py
A FastAPI-based AIKO agent that discovers 'PONG' via Zeroconf and sends 1000 ping-pong messages.
"""

import time
import asyncio
import logging
import socket
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser

# --- Configuration ---
AGENT_NAME = "PING"
AGENT_PORT = 8000
TARGET_AGENT_NAME = "PONG"
MAX_COUNT = 1000

# --- Setup logging ---
logging.basicConfig(filename="console.txt", level=logging.INFO)

app = FastAPI()
zeroconf = Zeroconf()
TARGET_URL = None

# --- Define message schema ---
class Message(BaseModel):
    message: str

# --- Register this service on LAN ---
def register_service():
    local_ip = socket.gethostbyname(socket.gethostname())
    service = ServiceInfo(
        type_="_aikoagent._tcp.local.",
        name=f"{AGENT_NAME}._aikoagent._tcp.local.",
        addresses=[socket.inet_aton(local_ip)],
        port=AGENT_PORT,
        properties={"role": "initiator"},
        server=f"{AGENT_NAME}.local.",
    )
    zeroconf.register_service(service)
    print(f"[{AGENT_NAME}] Registered on LAN at {local_ip}:{AGENT_PORT}")

# --- Discover pong agent ---
async def discover_target(timeout=3):
    global TARGET_URL

    class Listener:
        def __init__(self):
            self.info = None

        def add_service(self, zc, type_, name):
            if TARGET_AGENT_NAME in name:
                self.info = zc.get_service_info(type_, name)

    listener = Listener()
    browser = ServiceBrowser(zeroconf, "_aikoagent._tcp.local.", listener)
    for _ in range(timeout * 10):
        await asyncio.sleep(0.1)
        if listener.info:
            ip = socket.inet_ntoa(listener.info.addresses[0])
            port = listener.info.port
            TARGET_URL = f"http://{ip}:{port}/handle"
            print(f"[{AGENT_NAME}] Found {TARGET_AGENT_NAME} at {TARGET_URL}")
            return
    print(f"[{AGENT_NAME}] Could not discover {TARGET_AGENT_NAME}.")

# --- Message handler ---
@app.post("/handle")
async def handle_message(msg: Message):
    logging.info(f"[{AGENT_NAME}] Received: {msg.message} at {time.time()}")
    count = int(msg.message.split("#")[1])
    if count >= MAX_COUNT:
        return {"reply": "done"}
    next_msg = f"message #{count + 1}"
    await asyncio.sleep(0.01)
    if TARGET_URL:
        async with httpx.AsyncClient() as client:
            response = await client.post(TARGET_URL, json={"message": next_msg})
        logging.info(f"[{AGENT_NAME}] Sent: {next_msg} at {time.time()}")
        return response.json()
    else:
        return {"reply": "pong agent not available"}

# --- Startup: register, discover, and begin the conversation ---
@app.on_event("startup")
async def startup():
    register_service()
    await discover_target()
    if TARGET_URL:
        await asyncio.sleep(1)
        print(f"[{AGENT_NAME}] Starting message #0")
        async with httpx.AsyncClient() as client:
            await client.post(TARGET_URL, json={"message": "message #0"})
