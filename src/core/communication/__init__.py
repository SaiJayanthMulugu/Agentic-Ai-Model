"""
Agent Communication Module
===========================

Message bus and event system for agent-to-agent communication.
"""

from src.core.communication.message_bus import MessageBus
from src.core.communication.event_system import EventSystem

__all__ = [
    "MessageBus",
    "EventSystem",
]

