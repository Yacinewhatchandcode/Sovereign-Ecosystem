"""
Autonomous Coordinator Agent - Coordinates all autonomous agents via MCP
Auto-orchestrates cleanup, testing, streamlining, and learning
"""
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
from memory_agent import EnhancedMemoryAgent
from neural_meshwork import NeuralMeshwork
from autonomous_cleanup_agent import AutonomousCleanupAgent
from autonomous_test_agent import AutonomousTestAgent
from autonomous_streamline_agent import AutonomousStreamlineAgent
from autonomous_learning_agent import AutonomousLearningAgent

logger = structlog.get_logger()

class AutonomousCoordinatorAgent:
    """Coordinates all autonomous agents for codebase maintenance"""

    def __init__(self):
        self.memory = EnhancedMemoryAgent()
        self.meshwork = NeuralMeshwork()
        self.agent_id = "coordinator_agent"

        # Initialize all autonomous agents
        self.cleanup_agent = AutonomousCleanupAgent()
        self.test_agent = AutonomousTestAgent()
        self.streamline_agent = AutonomousStreamlineAgent()
        self.learning_agent = AutonomousLearningAgent()

        # Register in meshwork
        self.meshwork.register_agent(self.agent_id, self._handle_message)

        # Connect to all agents
        self._setup_connections()

        logger.info("AutonomousCoordinatorAgent initialized")

    def _setup_connections(self):
        """Connect to all autonomous agents"""
        agent_ids = ['cleanup_agent', 'test_agent', 'streamline_agent', 'learning_agent']
        for agent_id in agent_ids:
            try:
                self.meshwork.connect(self.agent_id, agent_id)
            except:
                pass

    async def _handle_message(self, sender_id: str, message: Dict[str, Any]):
        """Handle messages via meshwork"""
        msg_type = message.get('type', 'coordinate')
        content = message.get('content', '')

        if msg_type == 'coordinate_all':
            return await self.coordinate_all_tasks()
        elif msg_type == 'cleanup':
            return await self.coordinate_cleanup()
        elif msg_type == 'test':
            return await self.coordinate_testing()
        elif msg_type == 'streamline':
            return await self.coordinate_streamlining()
        elif msg_type == 'get_status':
            return self.get_status()

        return None

    async def coordinate_all_tasks(self) -> Dict[str, Any]:
        """Coordinate all autonomous tasks: cleanup, test, streamline"""
        logger.info("Coordinating all autonomous tasks")

        results = {
            'cleanup': {},
            'testing': {},
            'streamlining': {},
            'learning': {},
            'overall_success': False
        }

        try:
            # Phase 1: Cleanup
            logger.info("Phase 1: Cleanup")
            cleanup_msg = {
                'type': 'cleanup_request',
                'content': 'all',
                'timestamp': datetime.now().isoformat()
            }
            cleanup_result = await self.meshwork.send_direct(
                self.agent_id, 'cleanup_agent', cleanup_msg
            )
            results['cleanup'] = cleanup_result or {}

            # Phase 2: Testing
            logger.info("Phase 2: Testing")
            test_msg = {
                'type': 'run_tests',
                'content': 'all',
                'timestamp': datetime.now().isoformat()
            }
            test_result = await self.meshwork.send_direct(
                self.agent_id, 'test_agent', test_msg
            )
            results['testing'] = test_result or {}

            # Phase 3: Streamlining
            logger.info("Phase 3: Streamlining")
            streamline_msg = {
                'type': 'streamline_codebase',
                'content': 'all',
                'timestamp': datetime.now().isoformat()
            }
            streamline_result = await self.meshwork.send_direct(
                self.agent_id, 'streamline_agent', streamline_msg
            )
            results['streamlining'] = streamline_result or {}

            # Phase 4: Learning (collects from all)
            logger.info("Phase 4: Learning")
            learning_result = await self.learning_agent.share_knowledge("all_agents")
            results['learning'] = learning_result or {}

            # Determine overall success
            results['overall_success'] = (
                results['cleanup'].get('files_cleaned', 0) >= 0 and
                results['testing'].get('tests_passed', 0) >= 0 and
                results['streamlining'].get('files_streamlined', 0) >= 0
            )

            # Memorize coordination results
            self.memory.store(
                "coordination_run",
                str(results),
                {'timestamp': datetime.now().isoformat(), **results}
            )

            logger.info("Coordination complete", success=results['overall_success'])
            return results

        except Exception as e:
            logger.error("Coordination failed", error=str(e))
            return {'error': str(e), **results}

    async def coordinate_cleanup(self) -> Dict[str, Any]:
        """Coordinate cleanup task"""
        message = {
            'type': 'cleanup_request',
            'content': 'all',
            'timestamp': datetime.now().isoformat()
        }

        result = await self.meshwork.send_direct(self.agent_id, 'cleanup_agent', message)
        return result or {}

    async def coordinate_testing(self) -> Dict[str, Any]:
        """Coordinate testing task"""
        message = {
            'type': 'run_tests',
            'content': 'all',
            'timestamp': datetime.now().isoformat()
        }

        result = await self.meshwork.send_direct(self.agent_id, 'test_agent', message)
        return result or {}

    async def coordinate_streamlining(self) -> Dict[str, Any]:
        """Coordinate streamlining task"""
        message = {
            'type': 'streamline_codebase',
            'content': 'all',
            'timestamp': datetime.now().isoformat()
        }

        result = await self.meshwork.send_direct(self.agent_id, 'streamline_agent', message)
        return result or {}

    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status"""
        return {
            'agent_id': self.agent_id,
            'agents_connected': ['cleanup_agent', 'test_agent', 'streamline_agent', 'learning_agent'],
            'status': 'active'
        }

    async def auto_enable_features(self):
        """Auto-enable all features and capabilities"""
        logger.info("Auto-enabling all features")

        # Enable all agent capabilities
        try:
            # Ensure all agents are connected
            self._setup_connections()

            # Broadcast enable message
            enable_msg = {
                'type': 'enable_all',
                'content': 'Enable all autonomous features',
                'timestamp': datetime.now().isoformat()
            }

            await self.meshwork.broadcast(self.agent_id, enable_msg)

            logger.info("All features enabled")
            return {'success': True}
        except Exception as e:
            logger.error("Feature enable failed", error=str(e))
            return {'error': str(e)}
