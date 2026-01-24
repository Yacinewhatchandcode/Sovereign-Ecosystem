"""
Goal Orchestrator - Systematically leverages all agents toward specific goals
Enables Auto (AI assistant) to coordinate agents via MCP to achieve objectives
"""
import asyncio
from datetime import datetime
import structlog
import json

logger = structlog.get_logger()

class GoalOrchestrator:
    """Orchestrates agents systematically toward goals"""

    def __init__(self):
        self.registry = get_registry()
        self.network = get_network()
        self.orchestrator = OrchestratorAgent()
        self.active_goals = {}
        self.goal_history = []

    async def set_goal(self, goal_id: str, description: str, strategy: Optional[str] = None) -> Dict[str, Any]:
        """Set a goal and create execution plan"""
        goal = {
            'id': goal_id,
            'description': description,
            'strategy': strategy or 'auto',
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'agents_assigned': [],
            'tasks': [],
            'progress': 0.0
        }

        self.active_goals[goal_id] = goal
        self.goal_history.append(goal.copy())

        # Analyze goal and assign agents
        await self._assign_agents_to_goal(goal)

        logger.info("Goal set", goal_id=goal_id, description=description[:50])
        return goal

    async def _assign_agents_to_goal(self, goal: Dict[str, Any]):
        """Intelligently assign agents to goal based on goal description"""
        description_lower = goal['description'].lower()
        assigned = []

        # Always include orchestrator
        assigned.append('orch')

        # Get all available agents
        all_agents = {a['id']: a for a in self.registry.list_agents()}

        # Analyze goal requirements
        if any(kw in description_lower for kw in ['search', 'find', 'web', 'news', 'information']):
            assigned.extend(['search', 'cognitivesearch'])

        if any(kw in description_lower for kw in ['generate', 'create', 'write', 'response', 'text']):
            assigned.extend(['llm', 'orch'])

        if any(kw in description_lower for kw in ['cache', 'optimize', 'performance', 'speed']):
            assigned.extend(['cache', 'smartcache'])

        if any(kw in description_lower for kw in ['video', 'stream', 'generate video']):
            assigned.extend(['ultrafastorch', 'streaming', 'progressivestreaming'])

        if any(kw in description_lower for kw in ['memory', 'remember', 'context', 'learn']):
            assigned.extend(['enhancedmemory'])

        if any(kw in description_lower for kw in ['verify', 'validate', 'check', 'consensus']):
            assigned.extend(['consensus'])

        if any(kw in description_lower for kw in ['audio', 'voice', 'speech', 'tts']):
            assigned.extend(['tts'])

        # Remove duplicates
        goal['agents_assigned'] = list(set(assigned))
        logger.info("Agents assigned to goal", goal_id=goal['id'], agents=goal['agents_assigned'])

    async def execute_goal(self, goal_id: str) -> Dict[str, Any]:
        """Execute a goal by coordinating assigned agents"""
        if goal_id not in self.active_goals:
            return {'error': f'Goal {goal_id} not found'}

        goal = self.active_goals[goal_id]
        goal['status'] = 'executing'
        goal['started_at'] = datetime.now().isoformat()

        logger.info("Executing goal", goal_id=goal_id)

        # Break down goal into tasks
        tasks = await self._break_down_goal(goal)
        goal['tasks'] = tasks

        # Execute tasks systematically
        results = []
        for i, task in enumerate(tasks):
            task_result = await self._execute_task(goal_id, task, i + 1, len(tasks))
            results.append(task_result)
            goal['progress'] = (i + 1) / len(tasks) * 100

        goal['status'] = 'completed'
        goal['completed_at'] = datetime.now().isoformat()
        goal['results'] = results

        return goal

    async def _break_down_goal(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down goal into actionable tasks"""
        description = goal['description']
        tasks = []

        # Simple task breakdown based on goal description
        if 'search' in description.lower() or 'find' in description.lower():
            tasks.append({
                'id': f"{goal['id']}_task_1",
                'type': 'search',
                'agent': 'search',
                'action': 'Search for information related to goal',
                'description': description
            })

        if 'generate' in description.lower() or 'create' in description.lower():
            tasks.append({
                'id': f"{goal['id']}_task_2",
                'type': 'generate',
                'agent': 'llm',
                'action': 'Generate content based on goal',
                'description': description
            })

        if not tasks:
            # Default task: use orchestrator
            tasks.append({
                'id': f"{goal['id']}_task_1",
                'type': 'orchestrate',
                'agent': 'orch',
                'action': 'Coordinate agents to achieve goal',
                'description': description
            })

        return tasks

    async def _execute_task(self, goal_id: str, task: Dict[str, Any], task_num: int, total_tasks: int) -> Dict[str, Any]:
        """Execute a single task using assigned agent"""
        agent_id = task['agent']
        agent = self.registry.get_agent(agent_id)

        if not agent:
            return {'error': f'Agent {agent_id} not available', 'task': task}

        logger.info("Executing task", goal_id=goal_id, task=task['id'], agent=agent_id, progress=f"{task_num}/{total_tasks}")

        try:
            # Send task to agent
            message = f"GOAL: {goal_id}\nTASK: {task['action']}\nDESCRIPTION: {task['description']}"
            result = await self.network.send_message('goal_orchestrator', agent_id, message, msg_type='task')

            return {
                'task_id': task['id'],
                'agent': agent_id,
                'status': 'completed',
                'result': str(result) if result else 'Task executed',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error("Task execution failed", task=task['id'], error=str(e))
            return {
                'task_id': task['id'],
                'agent': agent_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def delegate_to_agent(self, agent_id: str, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delegate a specific task to an agent"""
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return {'error': f'Agent {agent_id} not found'}

        message = f"TASK: {task}"
        if context:
            message += f"\nCONTEXT: {json.dumps(context, indent=2)}"

        result = await self.network.send_message('goal_orchestrator', agent_id, message, msg_type='delegation')

        return {
            'agent': agent_id,
            'task': task,
            'result': str(result) if result else 'Task delegated',
            'timestamp': datetime.now().isoformat()
        }

    async def coordinate_agents(self, agents: List[str], task: str, strategy: str = 'parallel') -> Dict[str, Any]:
        """Coordinate multiple agents for a task"""
        logger.info("Coordinating agents", agents=agents, strategy=strategy)

        if strategy == 'parallel':
            # Execute in parallel
            tasks = [
                self.network.send_message('goal_orchestrator', agent_id, task, msg_type='coordination')
                for agent_id in agents
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Sequential execution
            results = []
            for agent_id in agents:
                result = await self.network.send_message('goal_orchestrator', agent_id, task, msg_type='coordination')
                results.append(result)

        return {
            'agents': agents,
            'strategy': strategy,
            'results': [str(r) if r else 'No response' for r in results],
            'timestamp': datetime.now().isoformat()
        }

    def get_goal_status(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a goal"""
        return self.active_goals.get(goal_id)

    def list_goals(self) -> List[Dict[str, Any]]:
        """List all goals"""
        return list(self.active_goals.values())

    def get_agent_recommendations(self, goal_description: str) -> List[str]:
        """Recommend agents for a goal"""
        goal = {'description': goal_description}
        self._assign_agents_to_goal(goal)
        return goal['agents_assigned']

# Global instance
_goal_orchestrator = None

def get_goal_orchestrator() -> GoalOrchestrator:
    """Get global goal orchestrator"""
    global _goal_orchestrator
    if _goal_orchestrator is None:
        _goal_orchestrator = GoalOrchestrator()
    return _goal_orchestrator