# README.md

# Purpose of this project

This project demonstrates a distributed local AI system architecture
featuring AIKO agents. The `PING` agent uses Zeroconf to discover a
`PONG` agent over a local network and sends up to 1000 messages using
FastAPI.

# Project structure (tree)

```
.
├── agent_ping.py
├── LICENSE
├── README.md
└── 2025-04-04 Distributed Local AI System.md
```

# Environment

This project was written specifically to run on macOS.

# Instructions for Terminal

## Dependency Installation

Create a virtual environment and install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn zeroconf httpx
```

## How to run it

Start the FastAPI server for the `PING` agent:

```bash
uvicorn agent_ping:app --host 0.0.0.0 --port 8000
```

This registers the `PING` service on your local network and begins
searching for a `PONG` agent via Zeroconf.

Once found, it will initiate a ping-pong message exchange up to 1000
messages. All communication is logged to `console.txt`.

Make sure the corresponding `PONG` agent is running on the same LAN.

---

Respectfully,  
Uki D. Lucas

