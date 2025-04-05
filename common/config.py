""" config.py
Loads configuration from config.yml for AIKO agents.
"""

import os
import yaml
from pydantic_settings import BaseSettings
# While agent now works, the pydantic==1.10.13 could break other packages 
# (e.g. langchain, ollama, chromadb) that depend on Pydantic 2.x.

# Define path to the config file
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "agent_ping", "config.yml"
)

# Load YAML into dictionary
def load_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Define a Pydantic model to enforce structure
class AgentSettings(BaseSettings):
    AGENT_NAME: str
    AGENT_PORT: int
    TARGET_AGENT_NAME: str
    MAX_COUNT: int
    LOG_FILE: str

# Load settings from YAML
settings = AgentSettings(**load_yaml(CONFIG_PATH))
