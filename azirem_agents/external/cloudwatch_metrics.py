"""
CloudWatch Metrics - Specialized CloudWatch integration for Agent View
Provides Agent View metrics, live widgets, and log stream monitoring.
"""
import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_CLOUDWATCH_NAMESPACE = os.getenv("AWS_CLOUDWATCH_NAMESPACE", "Agenti-ASCIA")


class CloudWatchMetrics:
    """Specialized CloudWatch metrics for Agent View"""
    
    def __init__(self, region: str = AWS_REGION, namespace: str = AWS_CLOUDWATCH_NAMESPACE):
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for CloudWatch metrics")
        
        self.region = region
        self.namespace = namespace
        self._cloudwatch = None
        self._logs = None
    
    def _get_cloudwatch_client(self):
        """Get or create CloudWatch client"""
        if self._cloudwatch is None:
            self._cloudwatch = boto3.client('cloudwatch', region_name=self.region)
        return self._cloudwatch
    
    def _get_logs_client(self):
        """Get or create CloudWatch Logs client"""
        if self._logs is None:
            self._logs = boto3.client('logs', region_name=self.region)
        return self._logs
    
    async def get_agent_view_metrics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get Agent View specific metrics (latency, tokens, errors)"""
        cloudwatch = self._get_cloudwatch_client()
        
        metrics = {}
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)
        
        # Agent-specific metrics
        metric_queries = [
            ('AgentLatency', 'Average'),
            ('AgentRequests', 'Sum'),
            ('AgentErrors', 'Sum'),
            ('TokenCount', 'Sum'),
            ('InvocationCount', 'Sum')
        ]
        
        for metric_name, stat in metric_queries:
            try:
                dimensions = []
                if agent_id:
                    dimensions.append({'Name': 'AgentId', 'Value': agent_id})
                
                response = cloudwatch.get_metric_statistics(
                    Namespace=self.namespace,
                    MetricName=metric_name,
                    Dimensions=dimensions,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=60,
                    Statistics=[stat]
                )
                
                datapoints = response.get('Datapoints', [])
                if datapoints:
                    latest = max(datapoints, key=lambda x: x['Timestamp'])
                    metrics[metric_name] = {
                        'value': latest.get(stat, 0),
                        'timestamp': latest['Timestamp'].isoformat(),
                        'unit': latest.get('Unit', 'Count')
                    }
            except ClientError as e:
                logger.debug(f"Failed to get metric {metric_name}", error=str(e))
        
        return metrics
    
    async def get_live_metrics(self, metric_names: List[str], 
                              period: int = 1) -> Dict[str, Any]:
        """Get live (non-aggregated) metrics for widgets"""
        cloudwatch = self._get_cloudwatch_client()
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=period * 10)  # Last 10 periods
        
        metrics = {}
        
        for metric_name in metric_names:
            try:
                response = cloudwatch.get_metric_statistics(
                    Namespace=self.namespace,
                    MetricName=metric_name,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=period,
                    Statistics=['Average', 'Sum', 'Maximum', 'Minimum', 'SampleCount']
                )
                
                datapoints = response.get('Datapoints', [])
                if datapoints:
                    # Sort by timestamp
                    datapoints.sort(key=lambda x: x['Timestamp'])
                    metrics[metric_name] = {
                        'datapoints': [
                            {
                                'timestamp': dp['Timestamp'].isoformat(),
                                'average': dp.get('Average'),
                                'sum': dp.get('Sum'),
                                'max': dp.get('Maximum'),
                                'min': dp.get('Minimum'),
                                'live_count': dp.get('SampleCount')
                            }
                            for dp in datapoints
                        ],
                        'unit': datapoints[0].get('Unit', 'Count')
                    }
            except ClientError as e:
                logger.debug(f"Failed to get live metric {metric_name}", error=str(e))
        
        return metrics
    
    async def publish_agent_metric(self, agent_id: str, metric_name: str, 
                                  value: float, unit: str = "Count"):
        """Publish agent-specific metric"""
        cloudwatch = self._get_cloudwatch_client()
        
        try:
            cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[{
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit,
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {'Name': 'AgentId', 'Value': agent_id}
                    ]
                }]
            )
            return True
        except ClientError as e:
            logger.error("Failed to publish agent metric", error=str(e))
            return False
    
    async def get_log_streams(self, log_group: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get CloudWatch log streams"""
        logs = self._get_logs_client()
        
        try:
            response = logs.describe_log_streams(
                logGroupName=log_group,
                orderBy='LastEventTime',
                descending=True,
                limit=limit
            )
            
            streams = []
            for stream in response.get('logStreams', []):
                streams.append({
                    'name': stream['logStreamName'],
                    'last_event': stream.get('lastEventTimestamp', 0),
                    'size': stream.get('storedBytes', 0)
                })
            
            return streams
        except ClientError as e:
            logger.error("Failed to get log streams", error=str(e))
            return []
    
    async def get_recent_logs(self, log_group: str, log_stream: Optional[str] = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent log events"""
        logs = self._get_logs_client()
        
        try:
            kwargs = {
                'logGroupName': log_group,
                'limit': limit
            }
            
            if log_stream:
                kwargs['logStreamName'] = log_stream
            
            response = logs.filter_log_events(**kwargs)
            
            events = []
            for event in response.get('events', []):
                events.append({
                    'timestamp': event['timestamp'],
                    'message': event['message'],
                    'log_stream': event.get('logStreamName', '')
                })
            
            return events
        except ClientError as e:
            logger.error("Failed to get recent logs", error=str(e))
            return []
