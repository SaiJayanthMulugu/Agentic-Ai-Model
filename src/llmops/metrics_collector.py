"""
Metrics Collector
=================

Collects and aggregates metrics.

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Metrics collection."""
    
    def collect_metrics(self, agent_id: str, operation: str, duration_ms: float, success: bool) -> None:
        """Collect a metric."""
        logger.debug(f"Metric: {agent_id} - {operation} - {duration_ms}ms - {success}")

