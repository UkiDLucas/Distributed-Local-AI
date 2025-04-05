""" message_schema.py
Defines a shared message schema for AIKO agent communication.
"""

from pydantic import BaseModel

class Message(BaseModel):
    message: str