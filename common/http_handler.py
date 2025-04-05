""" http_handler.py
Provides a reusable FastAPI route for handling AIKO-style messages
using the common run_action(message, user) API.
"""

from fastapi import APIRouter
from common.message_schema import Message
from typing import Callable

def build_handle_route(run_action_func: Callable):
    """
    Given a run_action function, builds a FastAPI router that can be
    included into an agent's app.
    """
    router = APIRouter()

    @router.post("/handle")
    async def handle(msg: Message):
        context_md, matched_files = run_action_func(msg.message, user={})
        return {
            "context_md": context_md,
            "matched_files": matched_files
        }

    return router