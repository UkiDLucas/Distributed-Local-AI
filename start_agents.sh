#!/bin/bash

# start_agents.sh
# Launch the PING agent for Distributed Local AI

# Optional: activate virtual environment if not already active
# source env_Distributed-Local-AI/bin/activate

echo "Starting PING agent..."
uvicorn agent_ping.agent_ping:app \
  --host 0.0.0.0 \
  --port 8000
