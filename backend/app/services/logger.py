from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models import AgentLog
import json
import os


class AgentLogger:
    """
    Logger for tracking agent activities and pipeline execution
    """
    
    def __init__(self):
        self.logs: List[AgentLog] = []
        
    def log(
        self, 
        agent_name: str, 
        status: str, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Add a log entry
        
        Args:
            agent_name: Name of the agent (Research, Copywriter, Editor)
            status: Status (started, processing, completed, error, revision_needed)
            message: Human-readable message
            data: Optional additional data
        """
        log_entry = AgentLog(
            agent_name=agent_name,
            status=status,
            message=message,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        self.logs.append(log_entry)
        
        # Also print to console for debugging
        print(f"[{log_entry.timestamp}] {agent_name} - {status}: {message}")
    
    def get_logs(self) -> List[AgentLog]:
        """Get all log entries"""
        return self.logs
    
    def save_to_file(self, filepath: str):
        """Save logs to a JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(
                [log.model_dump() for log in self.logs],
                f,
                indent=2
            )
    
    def clear(self):
        """Clear all logs"""
        self.logs = []