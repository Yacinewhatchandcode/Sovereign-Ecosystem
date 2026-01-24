"""
Real-Time Agent Monitor V1 - Enhanced with AWS CloudWatch Integration
Unified activity tracking with real-time metrics calculation and AWS integration.
"""
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import structlog
from dataclasses import dataclass
from enum import Enum
import os

logger = structlog.get_logger()

# Shared state file for cross-process communication
STATE_FILE = Path(__file__).parent / ".realtime_monitor_state.json"


class ActivityType(Enum):
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    AGENT_ANNOUNCEMENT = "agent_announcement"
    PROGRESS_UPDATE = "progress_update"
    QUALITY_METRIC = "quality_metric"
    AWS_METRIC = "aws_metric"  # New: AWS CloudWatch metrics
    BEDROCK_EVENT = "bedrock_event"  # New: Bedrock AgentCore events


@dataclass
class ActivityEvent:
    timestamp: float
    type: ActivityType
    agent_id: str
    file_path: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'type': self.type.value,
            'agent_id': self.agent_id,
            'file_path': self.file_path,
            'message': self.message,
            'data': self.data or {}
        }


class RealtimeAgentMonitorV1:
    """Enhanced real-time monitor with AWS CloudWatch integration"""
    
    def __init__(self):
        self.activities: List[ActivityEvent] = []
        self.subscribers: List[Callable] = []
        self.file_states: Dict[str, Dict[str, Any]] = {}
        self.agent_progress: Dict[str, Dict[str, Any]] = {}
        self.quality_metrics: Dict[str, float] = {
            'files_processed': 0,
            'files_cleaned': 0,
            'issues_fixed': 0,
            'optimizations_applied': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }
        # AWS metrics cache
        self.aws_metrics: Dict[str, Any] = {}
        self.aws_metrics_timestamp: float = 0
        self.running = False
        self._load_state()
        logger.info("RealtimeAgentMonitorV1 initialized")
    
    def _load_state(self):
        """Load state from file (for cross-process sharing)"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    self.quality_metrics = state.get('quality_metrics', self.quality_metrics)
                    self.file_states = state.get('file_states', {})
                    self.aws_metrics = state.get('aws_metrics', {})
                    # Convert file_states timestamps back to float
                    for key, value in self.file_states.items():
                        if 'last_modified' in value:
                            value['last_modified'] = float(value['last_modified'])
        except Exception as e:
            logger.debug("Could not load state", error=str(e))
    
    def _save_state(self):
        """Save state to file (for cross-process sharing)"""
        try:
            # Don't save file content to state file (too large)
            file_states_metadata = {}
            for key, value in self.file_states.items():
                file_states_metadata[key] = {
                    k: v for k, v in value.items() 
                    if k != 'last_content'  # Exclude content
                }
            
            state = {
                'quality_metrics': self.quality_metrics,
                'file_states': file_states_metadata,
                'aws_metrics': self.aws_metrics,
                'timestamp': time.time()
            }
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logger.debug("Could not save state", error=str(e))
    
    def subscribe(self, callback: Callable):
        """Subscribe to real-time updates"""
        self.subscribers.append(callback)
        logger.debug("New subscriber", total=len(self.subscribers))
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from updates"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def _broadcast(self, event: ActivityEvent):
        """Broadcast event to all subscribers"""
        event_dict = event.to_dict()
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_dict)
                else:
                    callback(event_dict)
            except Exception as e:
                logger.error("Broadcast failed", error=str(e))
    
    async def log_activity(self, activity_type: ActivityType, agent_id: str, 
                          file_path: Optional[str] = None, message: Optional[str] = None,
                          data: Optional[Dict[str, Any]] = None):
        """Log and broadcast an activity"""
        event = ActivityEvent(
            timestamp=time.time(),
            type=activity_type,
            agent_id=agent_id,
            file_path=file_path,
            message=message,
            data=data
        )
        
        self.activities.append(event)
        await self._broadcast(event)
        
        # Keep only last 1000 activities
        if len(self.activities) > 1000:
            self.activities = self.activities[-1000:]
        
        logger.debug("Activity logged", type=activity_type.value, agent=agent_id)
    
    async def track_file_change(self, file_path: str, agent_id: str, 
                               before_size: int, after_size: int,
                               changes: Dict[str, Any]):
        """Track file changes in real-time"""
        file_key = str(file_path)
        
        if file_key not in self.file_states:
            await self.log_activity(
                ActivityType.FILE_CREATED,
                agent_id,
                file_path=file_key,
                message=f"File created: {Path(file_key).name}",
                data={'size': after_size}
            )
        else:
            await self.log_activity(
                ActivityType.FILE_MODIFIED,
                agent_id,
                file_path=file_key,
                message=f"File modified: {Path(file_key).name}",
                data={
                    'before_size': before_size,
                    'after_size': after_size,
                    'size_change': after_size - before_size,
                    'changes': changes
                }
            )
        
        # Try to store file content for code learning viewer
        try:
            path = Path(file_key)
            if path.exists():
                current_content = path.read_text(encoding='utf-8')
                # Store content (but limit size to avoid memory issues)
                if len(current_content) < 100000:  # Only store files < 100KB
                    self.file_states[file_key] = {
                        'path': file_key,
                        'size': after_size,
                        'last_modified': time.time(),
                        'last_agent': agent_id,
                        'changes': changes,
                        'last_content': current_content
                    }
                else:
                    self.file_states[file_key] = {
                        'path': file_key,
                        'size': after_size,
                        'last_modified': time.time(),
                        'last_agent': agent_id,
                        'changes': changes
                    }
            else:
                self.file_states[file_key] = {
                    'path': file_key,
                    'size': after_size,
                    'last_modified': time.time(),
                    'last_agent': agent_id,
                    'changes': changes
                }
        except Exception as e:
            logger.debug("Could not store file content", error=str(e), file_path=file_key)
            self.file_states[file_key] = {
                'path': file_key,
                'size': after_size,
                'last_modified': time.time(),
                'last_agent': agent_id,
                'changes': changes
            }
        
        self._save_state()
    
    async def track_agent_progress(self, agent_id: str, progress: Dict[str, Any]):
        """Track agent progress in real-time"""
        self.agent_progress[agent_id] = {
            **progress,
            'timestamp': time.time(),
            'agent_id': agent_id
        }
        
        await self.log_activity(
            ActivityType.PROGRESS_UPDATE,
            agent_id,
            message=f"Progress update: {agent_id}",
            data=progress
        )
    
    async def update_quality_metrics(self, metrics: Dict[str, float]):
        """Update quality metrics"""
        for key, value in metrics.items():
            if key in self.quality_metrics:
                self.quality_metrics[key] += value
            else:
                self.quality_metrics[key] = value
        
        self._save_state()
        
        await self.log_activity(
            ActivityType.QUALITY_METRIC,
            "system",
            message="Quality metrics updated",
            data=self.quality_metrics.copy()
        )
    
    async def update_aws_metrics(self, metrics: Dict[str, Any]):
        """Update AWS CloudWatch metrics"""
        self.aws_metrics = metrics
        self.aws_metrics_timestamp = time.time()
        self._save_state()
        
        await self.log_activity(
            ActivityType.AWS_METRIC,
            "aws",
            message="AWS metrics updated",
            data=metrics
        )
    
    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage"""
        total_files = self.quality_metrics.get('files_processed', 0)
        if total_files == 0:
            return 0.0
        
        cleaned = self.quality_metrics.get('files_cleaned', 0)
        fixed = self.quality_metrics.get('issues_fixed', 0)
        
        base_progress = (cleaned / total_files * 100) if total_files > 0 else 0
        quality_bonus = min(fixed * 2, 20)
        
        return min(base_progress + quality_bonus, 100.0)
    
    def get_quality_score(self) -> float:
        """Calculate quality score (0-100)"""
        total_files = self.quality_metrics.get('files_processed', 0)
        if total_files == 0:
            return 0.0
        
        cleaned = self.quality_metrics.get('files_cleaned', 0)
        fixed = self.quality_metrics.get('issues_fixed', 0)
        optimized = self.quality_metrics.get('optimizations_applied', 0)
        tests_passed = self.quality_metrics.get('tests_passed', 0)
        tests_failed = self.quality_metrics.get('tests_failed', 0)
        
        total_tests = tests_passed + tests_failed
        test_score = (tests_passed / total_tests * 100) if total_tests > 0 else 50
        
        quality = (
            (cleaned / total_files * 40) +
            (min(fixed / max(total_files, 1) * 10, 30)) +
            (min(optimized / max(total_files, 1) * 5, 20)) +
            (test_score * 0.1)
        )
        
        return min(quality, 100.0)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current status summary"""
        self._load_state()  # Reload to get latest from other processes
        
        return {
            'progress_percentage': self.get_progress_percentage(),
            'quality_score': self.get_quality_score(),
            'metrics': self.quality_metrics.copy(),
            'aws_metrics': self.aws_metrics.copy() if self.aws_metrics else {},
            'files_tracked': len(self.file_states),
            'agents_active': len(self.agent_progress),
            'recent_activities': len([a for a in self.activities if time.time() - a.timestamp < 60]),
            'timestamp': time.time()
        }
    
    async def stream_activities(self, since: Optional[float] = None):
        """Stream activities since a timestamp"""
        if since is None:
            since = time.time() - 60  # Last minute
        
        for activity in self.activities:
            if activity.timestamp >= since:
                yield activity.to_dict()


# Global monitor instance
_monitor = None

def get_monitor() -> RealtimeAgentMonitorV1:
    """Get global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = RealtimeAgentMonitorV1()
    return _monitor
