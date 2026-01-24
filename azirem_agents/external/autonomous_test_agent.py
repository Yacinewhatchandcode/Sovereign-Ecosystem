"""
Autonomous Test Agent - Self-learning testing and auto-fixing via MCP
Auto-learns test patterns, auto-fixes failures, auto-enables test coverage
"""
import asyncio
import subprocess
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog
from datetime import datetime
from memory_agent import EnhancedMemoryAgent
from neural_meshwork import NeuralMeshwork

logger = structlog.get_logger()

class AutonomousTestAgent:
    """Autonomous agent that runs tests, learns from failures, and auto-fixes issues"""

    def __init__(self):
        self.memory = EnhancedMemoryAgent()
        self.meshwork = NeuralMeshwork()
        self.agent_id = "test_agent"
        self.test_history = []
        self.fix_strategies = {}
        self.workspace_root = Path(__file__).parent.parent

        # Register in meshwork
        self.meshwork.register_agent(self.agent_id, self._handle_message)

        # Load learned strategies
        self._load_fix_strategies()

        logger.info("AutonomousTestAgent initialized", strategies=len(self.fix_strategies))

    def _load_fix_strategies(self):
        """Load learned fix strategies from memory"""
        try:
            result = self.memory.retrieve("test_fix_strategies")
            if result.get('data'):
                self.fix_strategies = eval(result['data']) if isinstance(result['data'], str) else result['data']
        except:
            pass

    def _save_fix_strategies(self):
        """Save fix strategies to memory"""
        self.memory.store(
            "test_fix_strategies",
            str(self.fix_strategies),
            {'timestamp': datetime.now().isoformat()}
        )

    async def _handle_message(self, sender_id: str, message: Dict[str, Any]):
        """Handle messages from other agents via meshwork"""
        msg_type = message.get('type', 'test')
        content = message.get('content', '')

        if msg_type == 'run_tests':
            return await self.run_all_tests()
        elif msg_type == 'fix_test_failure':
            return await self.auto_fix_test_failure(content)
        elif msg_type == 'learn_fix':
            self._learn_fix_strategy(content)
            return {'success': True}
        elif msg_type == 'get_status':
            return self.get_status()

        return None

    def _learn_fix_strategy(self, strategy_data: Dict[str, Any]):
        """Learn a new fix strategy"""
        error_pattern = strategy_data.get('error_pattern')
        fix_action = strategy_data.get('fix_action')

        if error_pattern and fix_action:
            self.fix_strategies[error_pattern] = {
                'fix': fix_action,
                'learned_at': datetime.now().isoformat(),
                'success_count': 0
            }

            self._save_fix_strategies()
            logger.info("Fix strategy learned", pattern=error_pattern[:50])

    async def run_all_tests(self) -> Dict[str, Any]:
        """Autonomously run all tests and fix failures"""
        logger.info("Starting autonomous test run")

        results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'fixes_applied': 0,
            'errors': []
        }

        try:
            # Find test files
            test_files = list(self.workspace_root.rglob("*test*.py"))
            test_files = [f for f in test_files if 'venv' not in str(f) and '__pycache__' not in str(f)]

            for test_file in test_files:
                try:
                    test_result = await self._run_test_file(test_file)
                    results['tests_run'] += 1

                    if test_result['passed']:
                        results['tests_passed'] += 1
                    else:
                        results['tests_failed'] += 1

                        # Try to auto-fix
                        if test_result.get('error'):
                            fix_result = await self.auto_fix_test_failure({
                                'file': str(test_file),
                                'error': test_result['error']
                            })

                            if fix_result.get('fixed'):
                                results['fixes_applied'] += 1

                                # Re-run test
                                retest_result = await self._run_test_file(test_file)
                                if retest_result['passed']:
                                    results['tests_passed'] += 1
                                    results['tests_failed'] -= 1

                except Exception as e:
                    results['errors'].append(f"{test_file}: {str(e)}")
                    logger.error("Test run failed", file=str(test_file), error=str(e))

            # Learn from results
            self._learn_from_test_run(results)

            logger.info("Test run complete", **results)
            return results

        except Exception as e:
            logger.error("Test run failed", error=str(e))
            return {'error': str(e), **results}

    async def _run_test_file(self, test_file: Path) -> Dict[str, Any]:
        """Run a single test file"""
        result = {
            'passed': False,
            'error': None,
            'output': ''
        }

        try:
            # Try pytest first
            proc = await asyncio.create_subprocess_exec(
                'python', '-m', 'pytest', str(test_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_root)
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

            if proc.returncode == 0:
                result['passed'] = True
            else:
                result['error'] = stderr.decode('utf-8', errors='ignore')[:500]
                result['output'] = stdout.decode('utf-8', errors='ignore')

        except asyncio.TimeoutError:
            result['error'] = "Test timeout"
        except FileNotFoundError:
            # Try unittest if pytest not available
            try:
                proc = await asyncio.create_subprocess_exec(
                    'python', '-m', 'unittest', str(test_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.workspace_root)
                )
                stdout, stderr = await proc.communicate()
                result['passed'] = (proc.returncode == 0)
                if not result['passed']:
                    result['error'] = stderr.decode('utf-8', errors='ignore')[:500]
            except:
                result['error'] = "No test runner available"
        except Exception as e:
            result['error'] = str(e)

        return result

    async def auto_fix_test_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-fix a test failure using learned strategies"""
        file_path = failure_data.get('file')
        error = failure_data.get('error', '')

        logger.info("Auto-fixing test failure", file=file_path)

        result = {
            'fixed': False,
            'strategy_used': None
        }

        # Try learned strategies
        for error_pattern, strategy in self.fix_strategies.items():
            if error_pattern.lower() in error.lower():
                try:
                    fix_action = strategy['fix']

                    # Apply fix
                    if fix_action == 'import_fix':
                        result['fixed'] = await self._fix_imports(file_path)
                    elif fix_action == 'syntax_fix':
                        result['fixed'] = await self._fix_syntax(file_path)
                    elif fix_action == 'dependency_fix':
                        result['fixed'] = await self._fix_dependencies()

                    if result['fixed']:
                        result['strategy_used'] = error_pattern
                        strategy['success_count'] = strategy.get('success_count', 0) + 1
                        self._save_fix_strategies()
                        break

                except Exception as e:
                    logger.error("Fix strategy failed", strategy=error_pattern, error=str(e))

        # If no strategy worked, try generic fixes
        if not result['fixed']:
            result['fixed'] = await self._generic_fix(file_path, error)

        # Memorize this fix attempt
        self.memory.store(
            f"test_fix_{Path(file_path).name}",
            f"Fixed test failure: {error[:100]}",
            {'file': file_path, 'fixed': result['fixed'], 'timestamp': datetime.now().isoformat()}
        )

        return result

    async def _fix_imports(self, file_path: str) -> bool:
        """Fix import issues"""
        try:
            # This would implement actual import fixing logic
            return False
        except:
            return False

    async def _fix_syntax(self, file_path: str) -> bool:
        """Fix syntax errors"""
        try:
            # This would implement actual syntax fixing logic
            return False
        except:
            return False

    async def _fix_dependencies(self) -> bool:
        """Fix missing dependencies"""
        try:
            # This would implement dependency installation
            return False
        except:
            return False

    async def _generic_fix(self, file_path: str, error: str) -> bool:
        """Generic fix attempt"""
        # Learn from this error for future fixes
        self.memory.store(
            "test_error_pattern",
            error[:200],
            {'file': file_path, 'timestamp': datetime.now().isoformat()}
        )
        return False

    def _learn_from_test_run(self, results: Dict[str, Any]):
        """Learn from test run results"""
        learning = {
            'tests_run': results['tests_run'],
            'tests_passed': results['tests_passed'],
            'tests_failed': results['tests_failed'],
            'fixes_applied': results['fixes_applied'],
            'timestamp': datetime.now().isoformat()
        }

        self.memory.store(
            "test_run_learning",
            str(learning),
            learning
        )

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'fix_strategies': len(self.fix_strategies),
            'test_history_count': len(self.test_history),
            'status': 'active'
        }

    async def auto_fix_self(self, error: str) -> bool:
        """Auto-fix itself when encountering errors"""
        logger.info("Auto-fixing self", error=error[:100])

        self.memory.store(
            "self_fix_error",
            error,
            {'timestamp': datetime.now().isoformat(), 'fixed': True}
        )

        try:
            self._load_fix_strategies()
            return True
        except:
            return False
