"""
Base Agent
==========

Abstract base class for all agents in the MAS platform.

Features:
- Standard agent interface
- Message bus integration
- Shared memory access
- Event subscription
- Metrics collection
- Error handling

Author: AI Ops Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.core.communication.message_bus import MessageBus
from src.core.communication.event_system import EventSystem
from src.core.agent_memory import AgentMemory

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    """
    
    def __init__(self, agent_name: str, agent_id: Optional[str] = None):
        """
        Initialize BaseAgent.
        
        Args:
            agent_name: Agent name
            agent_id: Unique agent ID (auto-generated if not provided)
        """
        self.agent_name = agent_name
        self.agent_id = agent_id or str(uuid.uuid4())
        self.config_loader = ConfigLoader()
        self.message_bus = MessageBus()
        self.event_system = EventSystem()
        self.memory = AgentMemory()
        
        # Load agent-specific config
        agents_config = self.config_loader.load("agents.yaml")
        self.agent_config = agents_config.get("agents", {}).get(agent_name, {})
        
        self.enabled = self.agent_config.get("enabled", True)
        self.priority = self.agent_config.get("priority", 5)
        self.max_concurrent_tasks = self.agent_config.get("max_concurrent_tasks", 10)
        self.timeout_seconds = self.agent_config.get("timeout_seconds", 60)
        self.retry_count = self.agent_config.get("retry_count", 2)
        self.requires_approval = self.agent_config.get("requires_approval", False)
        
        logger.info(f"Initialized {self.agent_name} (ID: {self.agent_id})")
    
    @abstractmethod
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task. Must be implemented by subclasses.
        
        Args:
            task: Task dictionary with task details
            context: Optional context from previous agents
        
        Returns:
            Result dictionary with status and output
        """
        pass
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message from message bus.
        
        Args:
            message: Message dictionary
        
        Returns:
            Response dictionary
        """
        try:
            task = message.get("content", {})
            context = message.get("context", {})
            
            # Process the task
            result = self.process(task, context)
            
            # Mark message as processed
            self.message_bus.mark_message_processed(message["message_id"], success=True)
            
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} failed to handle message: {e}")
            self.message_bus.mark_message_processed(
                message["message_id"],
                success=False,
                error_message=str(e)
            )
            raise
    
    def send_message(
        self,
        to_agent: str,
        content: Dict[str, Any],
        message_type: str = "request",
        correlation_id: Optional[str] = None,
        priority: int = 5
    ) -> str:
        """
        Send message to another agent.
        
        Args:
            to_agent: Recipient agent name
            content: Message content
            message_type: Message type
            correlation_id: Correlation ID
            priority: Message priority
        
        Returns:
            Message ID
        """
        return self.message_bus.send_message(
            from_agent=self.agent_name,
            to_agent=to_agent,
            content=content,
            message_type=message_type,
            correlation_id=correlation_id,
            priority=priority
        )
    
    def receive_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Receive pending messages.
        
        Args:
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of messages
        """
        return self.message_bus.receive_messages(self.agent_name, limit=limit)
    
    def store_memory(self, key: str, value: Any, ttl_hours: int = 24) -> None:
        """
        Store data in shared memory.
        
        Args:
            key: Memory key
            value: Memory value
            ttl_hours: Time to live in hours
        """
        self.memory.store(key, value, self.agent_name, ttl_hours)
    
    def retrieve_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve data from shared memory.
        
        Args:
            key: Memory key
        
        Returns:
            Memory value or None
        """
        return self.memory.retrieve(key)
    
    def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """
        Publish an event.
        
        Args:
            event_type: Event type
            event_data: Event data
        
        Returns:
            Event ID
        """
        return self.event_system.publish_event(
            event_type=event_type,
            source_agent=self.agent_name,
            event_data=event_data
        )
    
    def subscribe_to_events(self, event_types: List[str]) -> None:
        """
        Subscribe to event types.
        
        Args:
            event_types: List of event types to subscribe to
        """
        for event_type in event_types:
            self.event_system.subscribe_to_event(self.agent_id, event_type)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status.
        
        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "enabled": self.enabled,
            "priority": self.priority,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "timeout_seconds": self.timeout_seconds,
            "requires_approval": self.requires_approval
        }

