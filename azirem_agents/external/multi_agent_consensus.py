"""
Multi-Agent Consensus System - Like LangGraph/AutoGen
Agents verify each other's work and reach consensus on code changes
"""
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class ConsensusStatus(Enum):
    PENDING = "pending"
    AGREED = "agreed"
    DISAGREED = "disagreed"
    NEEDS_REVIEW = "needs_review"

@dataclass
class CodeChangeProposal:
    """A proposed code change from an agent"""
    agent_id: str
    file_path: str
    change_type: str
    before: str
    after: str
    confidence: float
    reasoning: str
    timestamp: float

@dataclass
class ConsensusResult:
    """Result of multi-agent consensus"""
    status: ConsensusStatus
    final_change: Optional[CodeChangeProposal]
    votes: Dict[str, bool]  # agent_id -> agree/disagree
    confidence: float
    message: str

class MultiAgentConsensus:
    """Multi-agent consensus system for code verification"""
    
    def __init__(self, agents: List[str], threshold: float = 0.7):
        self.agents = agents
        self.threshold = threshold
        self.proposals: Dict[str, List[CodeChangeProposal]] = {}
        self.consensus_history: List[ConsensusResult] = []
    
    async def propose_change(self, proposal: CodeChangeProposal) -> ConsensusResult:
        """Propose a code change and get consensus from other agents"""
        file_key = proposal.file_path
        
        if file_key not in self.proposals:
            self.proposals[file_key] = []
        
        self.proposals[file_key].append(proposal)
        
        # Get votes from other agents
        votes = await self._get_agent_votes(proposal)
        
        # Calculate consensus
        agree_count = sum(1 for v in votes.values() if v)
        total_votes = len(votes)
        agreement_ratio = agree_count / total_votes if total_votes > 0 else 0.0
        
        # Calculate final confidence
        final_confidence = (proposal.confidence + agreement_ratio) / 2
        
        if agreement_ratio >= self.threshold and final_confidence >= 0.7:
            status = ConsensusStatus.AGREED
            message = f"Consensus reached: {agree_count}/{total_votes} agents agree"
        elif agreement_ratio >= 0.5:
            status = ConsensusStatus.NEEDS_REVIEW
            message = f"Partial consensus: {agree_count}/{total_votes} agents agree - needs review"
        else:
            status = ConsensusStatus.DISAGREED
            message = f"No consensus: only {agree_count}/{total_votes} agents agree"
        
        result = ConsensusResult(
            status=status,
            final_change=proposal if status == ConsensusStatus.AGREED else None,
            votes=votes,
            confidence=final_confidence,
            message=message
        )
        
        self.consensus_history.append(result)
        logger.info("Consensus reached", 
                   file=proposal.file_path,
                   status=status.value,
                   confidence=final_confidence,
                   agreement=agreement_ratio)
        
        return result
    
    async def _get_agent_votes(self, proposal: CodeChangeProposal) -> Dict[str, bool]:
        """Get votes from other agents on a proposal"""
        votes = {}
        
        # Simulate agent verification (in real implementation, agents would verify)
        for agent_id in self.agents:
            if agent_id == proposal.agent_id:
                continue  # Skip proposing agent
            
            # Agent verifies the change
            vote = await self._agent_verify_change(agent_id, proposal)
            votes[agent_id] = vote
        
        return votes
    
    async def _agent_verify_change(self, agent_id: str, proposal: CodeChangeProposal) -> bool:
        """An agent verifies a proposed change"""
        # Simulate verification logic
        # In real implementation, each agent would:
        # 1. Parse the code change
        # 2. Check for syntax errors
        # 3. Verify the change makes sense
        # 4. Check if it improves code quality
        
        # For now, use confidence-based voting
        # Agents with higher confidence in their own analysis vote more strictly
        if proposal.confidence >= 0.9:
            return True  # High confidence changes are usually good
        elif proposal.confidence >= 0.7:
            # Medium confidence - check if change is reasonable
            # Check if it's a formatting/cleanup change (usually safe)
            if proposal.change_type in ['formatting', 'imports', 'spacing']:
                return True
            return False  # Be conservative for other changes
        else:
            return False  # Low confidence changes need more review
    
    def get_consensus_stats(self) -> Dict[str, Any]:
        """Get consensus statistics"""
        total = len(self.consensus_history)
        if total == 0:
            return {'total': 0}
        
        agreed = sum(1 for r in self.consensus_history if r.status == ConsensusStatus.AGREED)
        disagreed = sum(1 for r in self.consensus_history if r.status == ConsensusStatus.DISAGREED)
        needs_review = sum(1 for r in self.consensus_history if r.status == ConsensusStatus.NEEDS_REVIEW)
        
        avg_confidence = sum(r.confidence for r in self.consensus_history) / total
        
        return {
            'total': total,
            'agreed': agreed,
            'disagreed': disagreed,
            'needs_review': needs_review,
            'agreement_rate': agreed / total if total > 0 else 0,
            'avg_confidence': avg_confidence
        }
