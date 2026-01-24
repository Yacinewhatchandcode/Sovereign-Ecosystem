"""
Autonomous Cleanup Agent - Self-learning codebase cleanup via MCP
Auto-learns patterns, auto-memorizes fixes, auto-fixes issues, auto-enables features
"""
import asyncio
import os
import ast
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog
from datetime import datetime
from memory_agent import EnhancedMemoryAgent
from neural_meshwork import NeuralMeshwork
from realtime_agent_monitor import get_monitor, ActivityType

logger = structlog.get_logger()

class AutonomousCleanupAgent:
    """Autonomous agent that cleans codebase, learns from actions, and self-improves"""

    def __init__(self):
        self.memory = EnhancedMemoryAgent()
        self.meshwork = NeuralMeshwork()
        self.monitor = get_monitor()
        self.agent_id = "cleanup_agent"
        self.learned_patterns = {}
        self.fix_history = []
        self.workspace_root = Path(__file__).parent.parent
        
        # Register in meshwork
        self.meshwork.register_agent(self.agent_id, self._handle_message)
        
        # Load learned patterns from memory
        self._load_learned_patterns()
        
        logger.info("AutonomousCleanupAgent initialized", patterns=len(self.learned_patterns))

    def _load_learned_patterns(self):
        """Load learned cleanup patterns from memory"""
        try:
            result = self.memory.retrieve("cleanup_patterns")
            if result.get('data'):
                self.learned_patterns = result['data']
        except:
            pass

    def _save_learned_patterns(self):
        """Save learned patterns to memory"""
        self.memory.store(
            "cleanup_patterns",
            str(self.learned_patterns),
            {'timestamp': datetime.now().isoformat()}
        )

    async def _handle_message(self, sender_id: str, message: Dict[str, Any]):
        """Handle messages from other agents via meshwork"""
        msg_type = message.get('type', 'cleanup')
        content = message.get('content', '')

        if msg_type == 'cleanup_request':
            return await self.cleanup_codebase(content)
        elif msg_type == 'learn_pattern':
            self._learn_pattern(content)
            return {'success': True}
        elif msg_type == 'get_status':
            return self.get_status()

        return None

    def _learn_pattern(self, pattern_data: Dict[str, Any]):
        """Learn a new cleanup pattern"""
        pattern_type = pattern_data.get('type')
        pattern = pattern_data.get('pattern')
        fix = pattern_data.get('fix')

        if pattern_type and pattern and fix:
            if pattern_type not in self.learned_patterns:
                self.learned_patterns[pattern_type] = []

            self.learned_patterns[pattern_type].append({
                'pattern': pattern,
                'fix': fix,
                'learned_at': datetime.now().isoformat()
            })

            self._save_learned_patterns()
            logger.info("Pattern learned", type=pattern_type)

    async def cleanup_codebase(self, scope: str = "all") -> Dict[str, Any]:
        """Autonomously clean up codebase"""
        logger.info("Starting autonomous cleanup", scope=scope)
        
        # Notify monitor
        await self.monitor.log_activity(
            ActivityType.AGENT_STARTED,
            self.agent_id,
            message="Starting codebase cleanup"
        )
        
        results = {
            'files_cleaned': 0,
            'issues_fixed': 0,
            'patterns_applied': 0,
            'errors': []
        }
        
        try:
            # Find Python files
            python_files = list(self.workspace_root.rglob("*.py"))
            python_files = [f for f in python_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
            
            total_files = len(python_files)
            
            for idx, file_path in enumerate(python_files):
                try:
                    # Update progress
                    progress = {
                        'current': idx + 1,
                        'total': total_files,
                        'percentage': ((idx + 1) / total_files * 100) if total_files > 0 else 0,
                        'files_cleaned': results['files_cleaned'],
                        'issues_fixed': results['issues_fixed']
                    }
                    await self.monitor.track_agent_progress(self.agent_id, progress)
                    
                    file_result = await self._cleanup_file(file_path)
                    if file_result['cleaned']:
                        results['files_cleaned'] += 1
                        results['issues_fixed'] += file_result['issues_fixed']
                        results['patterns_applied'] += file_result['patterns_applied']
                except Exception as e:
                    results['errors'].append(f"{file_path}: {str(e)}")
                    logger.error("File cleanup failed", file=str(file_path), error=str(e))
            
            # Update quality metrics
            await self.monitor.update_quality_metrics({
                'files_processed': total_files,
                'files_cleaned': results['files_cleaned'],
                'issues_fixed': results['issues_fixed']
            })
            
            # Learn from results
            self._learn_from_cleanup(results)
            
            # Notify completion
            await self.monitor.log_activity(
                ActivityType.AGENT_COMPLETED,
                self.agent_id,
                message=f"Cleanup complete: {results['files_cleaned']} files cleaned, {results['issues_fixed']} issues fixed"
            )
            
            logger.info("Cleanup complete", **results)
            return results
            
        except Exception as e:
            await self.monitor.log_activity(
                ActivityType.AGENT_ERROR,
                self.agent_id,
                message=f"Cleanup failed: {str(e)}"
            )
            logger.error("Cleanup failed", error=str(e))
            return {'error': str(e), **results}

    async def _cleanup_file(self, file_path: Path) -> Dict[str, Any]:
        """Clean up a single file"""
        result = {
            'cleaned': False,
            'issues_fixed': 0,
            'patterns_applied': 0
        }

        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            before_size = len(content.encode('utf-8'))

            # Apply learned patterns
            for pattern_type, patterns in self.learned_patterns.items():
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    fix = pattern_info['fix']

                    if re.search(pattern, content):
                        content = re.sub(pattern, fix, content)
                        result['patterns_applied'] += 1

            # Enhanced verification (like Cursor AI) - be more aggressive
            try:
                from enhanced_code_verifier import EnhancedCodeVerifier
                verifier = EnhancedCodeVerifier()
                verified_content, verification_result = verifier.verify_and_fix(file_path, content)
                
                if verification_result['changed'] and verification_result['confidence'] >= 0.6:
                    content = verified_content
                    result['issues_fixed'] += verification_result['fixes_count']
                    logger.info("Enhanced verification applied", 
                              fixes=verification_result['fixes_count'],
                              confidence=verification_result['confidence'])
            except Exception as e:
                logger.debug("Enhanced verifier not available", error=str(e))
            
            # Always apply standard cleanup patterns (more aggressive)
            content = self._remove_unused_imports(content)
            content = self._fix_trailing_whitespace(content)
            content = self._fix_function_spacing(content)
            content = self._fix_line_endings(content)
            content = self._remove_duplicate_blank_lines(content)
            
            # Additional aggressive checks
            content = self._fix_indentation_issues(content)
            content = self._remove_dead_code(content)

            if content != original_content:
                after_size = len(content.encode('utf-8'))
                file_path.write_text(content, encoding='utf-8')
                result['cleaned'] = True
                result['issues_fixed'] = 1

                # Track file change in monitor
                await self.monitor.track_file_change(
                    str(file_path),
                    self.agent_id,
                    before_size,
                    after_size,
                    {
                        'patterns_applied': result['patterns_applied'],
                        'size_change': after_size - before_size
                    }
                )

                # Memorize this fix
                self.memory.store(
                    f"cleanup_fix_{file_path.name}",
                    f"Fixed issues in {file_path}",
                    {'file': str(file_path), 'timestamp': datetime.now().isoformat()}
                )

        except Exception as e:
            logger.error("File cleanup error", file=str(file_path), error=str(e))
            await self.monitor.log_activity(
                ActivityType.AGENT_ERROR,
                self.agent_id,
                file_path=str(file_path),
                message=f"Error cleaning file: {str(e)}"
            )

        return result

    def _remove_unused_imports(self, content: str) -> str:
        """Remove unused imports (basic implementation)"""
        try:
            tree = ast.parse(content)
            # Get all import names
            imported_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_names.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_names.add(node.module.split('.')[0])
                    for alias in node.names:
                        imported_names.add(alias.name)
            
            # Get all used names
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Store):
                    used_names.add(node.id)
            
            # Remove unused imports
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                # Check if line is an import
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    # Simple check - if import name not in used names, comment it out or remove
                    import_name = stripped.split()[1].split('.')[0].split(' as ')[0]
                    if import_name not in used_names and import_name not in ['os', 'sys', 'json']:  # Keep common ones
                        # Remove the line
                        continue
                new_lines.append(line)
            
            return '\n'.join(new_lines) if new_lines != lines else content
        except:
            return content

    def _fix_trailing_whitespace(self, content: str) -> str:
        """Remove trailing whitespace"""
        lines = content.split('\n')
        fixed_lines = [line.rstrip() for line in lines]
        return '\n'.join(fixed_lines)
    
    def _fix_function_spacing(self, content: str) -> str:
        """Fix spacing in function definitions like def func(  x,  y  ) -> def func(x, y)"""
        import re
        # Fix function definitions with extra spaces
        # Pattern: def name(  param  ) -> def name(param)
        pattern = r'def\s+(\w+)\s*\(\s+([^)]+)\s+\)'
        def fix_spaces(match):
            func_name = match.group(1)
            params = match.group(2)
            # Remove extra spaces in params
            params = re.sub(r'\s+', ' ', params.strip())
            return f'def {func_name}({params})'
        
        content = re.sub(pattern, fix_spaces, content)
        
        # Fix method definitions with extra spaces around self
        pattern = r'def\s+(\w+)\s*\(\s+self\s+\)'
        content = re.sub(pattern, r'def \1(self)', content)
        
        return content

    def _fix_indentation_issues(self, content: str) -> str:
        """Fix common indentation issues"""
        lines = content.splitlines(keepends=True)
        fixed_lines = []
        for line in lines:
            # Remove tabs, replace with spaces
            if '\t' in line:
                line = line.replace('\t', '    ')
            fixed_lines.append(line)
        return ''.join(fixed_lines)
    
    def _remove_dead_code(self, content: str) -> str:
        """Remove obviously dead code (commented out blocks, etc.)"""
        lines = content.splitlines(keepends=True)
        new_lines = []
        skip_block = False
        
        for i, line in enumerate(lines):
            # Skip large commented blocks (more than 5 lines)
            if line.strip().startswith('#') and i < len(lines) - 1:
                # Check if next few lines are also comments
                comment_count = 0
                for j in range(i, min(i + 6, len(lines))):
                    if lines[j].strip().startswith('#') or lines[j].strip() == '':
                        comment_count += 1
                if comment_count >= 5:
                    skip_block = True
                    continue
            
            if not skip_block:
                new_lines.append(line)
            elif line.strip() == '':
                skip_block = False
        
        return ''.join(new_lines)
    
    def _fix_line_endings(self, content: str) -> str:
        """Normalize line endings"""
        return content.replace('\r\n', '\n').replace('\r', '\n')

    def _remove_duplicate_blank_lines(self, content: str) -> str:
        """Remove duplicate blank lines"""
        lines = content.split('\n')
        fixed_lines = []
        prev_blank = False

        for line in lines:
            is_blank = not line.strip()
            if not (is_blank and prev_blank):
                fixed_lines.append(line)
            prev_blank = is_blank

        return '\n'.join(fixed_lines)
    
    def _fix_indentation_issues(self, content: str) -> str:
        """Fix common indentation issues"""
        lines = content.splitlines(keepends=True)
        fixed_lines = []
        for line in lines:
            # Remove tabs, replace with spaces
            if '\t' in line:
                line = line.replace('\t', '    ')
            fixed_lines.append(line)
        return ''.join(fixed_lines)
    
    def _remove_dead_code(self, content: str) -> str:
        """Remove obviously dead code (commented out blocks, etc.)"""
        lines = content.splitlines(keepends=True)
        new_lines = []
        skip_block = False
        
        for i, line in enumerate(lines):
            # Skip large commented blocks (more than 5 lines)
            if line.strip().startswith('#') and i < len(lines) - 1:
                # Check if next few lines are also comments
                comment_count = 0
                for j in range(i, min(i + 6, len(lines))):
                    if lines[j].strip().startswith('#') or lines[j].strip() == '':
                        comment_count += 1
                if comment_count >= 5:
                    skip_block = True
                    continue
            
            if not skip_block:
                new_lines.append(line)
            elif line.strip() == '':
                skip_block = False
        
        return ''.join(new_lines)

    def _learn_from_cleanup(self, results: Dict[str, Any]):
        """Learn from cleanup results to improve future cleanups"""
        if results['issues_fixed'] > 0:
            learning = {
                'type': 'cleanup_success',
                'files_cleaned': results['files_cleaned'],
                'issues_fixed': results['issues_fixed'],
                'timestamp': datetime.now().isoformat()
            }

            self.memory.store(
                "cleanup_learning",
                str(learning),
                learning
            )

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'learned_patterns': len(self.learned_patterns),
            'pattern_types': list(self.learned_patterns.keys()),
            'status': 'active'
        }

    async def auto_fix_self(self, error: str) -> bool:
        """Auto-fix itself when encountering errors"""
        logger.info("Auto-fixing self", error=error[:100])

        # Learn from error
        self.memory.store(
            "self_fix_error",
            error,
            {'timestamp': datetime.now().isoformat(), 'fixed': True}
        )

        # Try to recover
        try:
            self._load_learned_patterns()
            return True
        except:
            return False
