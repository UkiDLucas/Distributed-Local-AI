#!/bin/bash

# Launch both PING and PONG agents for Distributed Local AI

# Optional: activate virtual environment
# source env_Distributed-Local-AI/bin/activate

# Clear old logs
> console.txt

# Reset any stale mDNS registrations
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

echo "Starting PING agent..."
uvicorn agent_ping.agent_ping:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-config logging.ini >> console.txt 2>&1 &

echo "Starting PONG agent..."
uvicorn agent_pong.agent_pong:app \
  --host 0.0.0.0 \
  --port 8001 \
  --log-config logging.ini >> console.txt 2>&1 &

wait
echo "Both agents are running."
tail -f console.txt