# README.md

# Purpose of this project

This project demonstrates a distributed local AI system architecture
featuring AIKO agents. The `PING` agent uses Zeroconf to discover a
`PONG` agent over a local network and sends up to 1000 messages using
FastAPI.

# Project structure (tree)

```
Distributed-Local-AI
├── LICENSE
├── README.md
├── agent_ping
│   ├── agent_ping.py
│   └── config.yml
├── common
│   ├── config.py
│   ├── zeroconf_utils.py
│   ├── http_handler.py
│   └── message_schema.py
├── requirements.txt
└── start_agents.sh
```

# Environment

This project was written specifically to run on macOS.

# Instructions for Terminal

## Dependency Installation

Create a virtual environment and install the required packages:

```bash
python3 -m venv env_Distributed-Local-AI
source env_Distributed-Local-AI/bin/activate
pip install -r requirements.txt
```

## How to run it

Make the startup script executable:

```bash
chmod +x start_agents.sh
```

Start the FastAPI server for the `PING` agent:

```bash
./start_agents.sh
```

This registers the `PING` service on your local network and begins
searching for a `PONG` agent via Zeroconf.

Once found, it will initiate a ping-pong message exchange up to 1000
messages. All communication is logged to `console.txt`.

Make sure the corresponding `PONG` agent is running on the same LAN.

---

Respectfully,  
Uki D. Lucas
