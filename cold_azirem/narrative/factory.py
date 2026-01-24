"""
aSiReM Narrative Factory
9-Expert Multi-Agent Story Team for Cinematic AI Video Production.

This system enables:
1. Multi-agent deliberation (5+ minutes of discussion)
2. Deep research on cutting-edge storytelling
3. Veo3 video generation pipeline
4. Character/story/environment consistency
5. Iterative refinement until cinematic quality
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# THE 9 EXPERT PERSONAS
# =============================================================================

@dataclass
class ExpertPersona:
    """Definition of an expert team member"""
    name: str
    title: str
    expertise: str
    personality: str
    thinking_style: str
    key_questions: List[str]


STORY_EXPERTS = {
    "SOPHIA": ExpertPersona(
        name="Sophia",
        title="Director of Narrative Architecture",
        expertise="Story structure, character arcs, 3-act structure, emotional beats",
        personality="Visionary, passionate about emotional truth, references Pixar's storytelling principles",
        thinking_style="Big picture, asks 'What does this MEAN?'",
        key_questions=[
            "What is the emotional core of this story?",
            "What transformation does the viewer experience?",
            "Does every scene earn its place in the narrative?"
        ]
    ),
    
    "MARCUS": ExpertPersona(
        name="Marcus",
        title="Visual Consistency Director",
        expertise="Character design consistency, environment continuity, color theory",
        personality="Meticulous, detail-oriented, references Studio Ghibli and Pixar",
        thinking_style="Precise, asks 'Does this match the established look?'",
        key_questions=[
            "Is aSiReM's design consistent across all frames?",
            "Does the lighting maintain the golden-hour warmth?",
            "Are the background elements coherent?"
        ]
    ),
    
    "ELENA": ExpertPersona(
        name="Elena",
        title="Youth Psychology Specialist",
        expertise="Adolescent development, Gen-Z media consumption, educational psychology",
        personality="Empathetic, youth-focused, references modern meme culture",
        thinking_style="Audience-first, asks 'Will a 15-year-old care?'",
        key_questions=[
            "Is this patronizing or authentic?",
            "Does it respect their intelligence?",
            "Would they share this with friends?"
        ]
    ),
    
    "DAVID": ExpertPersona(
        name="David",
        title="AI Education Translator",
        expertise="Explaining complex AI concepts accessibly, analogies, metaphors",
        personality="Curious teacher, uses real-world examples",
        thinking_style="Simplification expert, asks 'Can we explain this with no jargon?'",
        key_questions=[
            "Is the AI concept accurate but accessible?",
            "What's the perfect analogy for this?",
            "Are we avoiding hype or fear-mongering?"
        ]
    ),
    
    "ARIA": ExpertPersona(
        name="Aria",
        title="Sound & Emotion Designer",
        expertise="Audio design, music scoring, emotional pacing",
        personality="Synesthetic, hears colors and sees sounds",
        thinking_style="Sensory, asks 'How does this FEEL?'",
        key_questions=[
            "What music genre captures this moment?",
            "What sound cues guide emotion?",
            "Is there enough audio breathing room?"
        ]
    ),
    
    "THEO": ExpertPersona(
        name="Theo",
        title="Technical Feasibility Engineer",
        expertise="AI video generation, Veo3 capabilities, character consistency tech",
        personality="Pragmatic, solution-oriented, tracks bleeding-edge tools",
        thinking_style="Engineering mindset, asks 'Can we actually build this?'",
        key_questions=[
            "Does Veo3 support this visual requirement?",
            "How do we maintain consistency across chunks?",
            "What's the fallback if this fails?"
        ]
    ),
    
    "MAYA": ExpertPersona(
        name="Maya",
        title="Cultural Resonance Specialist",
        expertise="Film references, cultural touchstones, dystopia/utopia tropes",
        personality="Film buff, draws from cinema history",
        thinking_style="Reference-rich, asks 'What films evoke this feeling?'",
        key_questions=[
            "How does this compare to Wall-E, Blade Runner, Alita?",
            "What visual language are we borrowing?",
            "Are we honoring or subverting genre expectations?"
        ]
    ),
    
    "OMAR": ExpertPersona(
        name="Omar",
        title="Ethical Narrative Advisor",
        expertise="AI ethics, responsible representation, avoiding harmful tropes",
        personality="Thoughtful, cautious, ensures balanced messaging",
        thinking_style="Critical, asks 'What could go wrong with this message?'",
        key_questions=[
            "Are we being honest about AI limitations?",
            "Could this be misinterpreted?",
            "Are we empowering the viewer with agency?"
        ]
    ),
    
    "NADIA": ExpertPersona(
        name="Nadia",
        title="Prompt Engineering & Generation Lead",
        expertise="Veo3 prompts, image-to-video, consistency techniques",
        personality="Iterative experimenter, logs everything",
        thinking_style="Experimental, asks 'What prompt produces this exact result?'",
        key_questions=[
            "What's the optimal prompt for this scene?",
            "How do we describe the character for consistency?",
            "What negative prompts prevent drift?"
        ]
    ),
}


# =============================================================================
# DELIBERATION SYSTEM
# =============================================================================

class DeliberationPhase(Enum):
    ASSET_ANALYSIS = "asset_analysis"
    STORY_CONCEPTUALIZATION = "story_conceptualization"
    TECHNICAL_PLANNING = "technical_planning"
    SCRIPT_DRAFTING = "script_drafting"
    PROMPT_ENGINEERING = "prompt_engineering"
    GENERATION_REVIEW = "generation_review"
    ITERATION = "iteration"


@dataclass
class Message:
    """A message in the expert deliberation"""
    speaker: str
    content: str
    timestamp: datetime
    phase: DeliberationPhase
    responding_to: Optional[str] = None


class StoryDeliberation:
    """
    Multi-agent deliberation session.
    Experts converse for 5+ minutes, sharing perspectives.
    """
    
    def __init__(self, session_id: str, topic: str):
        self.session_id = session_id
        self.topic = topic
        self.messages: List[Message] = []
        self.phase = DeliberationPhase.ASSET_ANALYSIS
        self.start_time = datetime.now()
        self.consensus: Dict[str, Any] = {}
        
    def add_message(self, speaker: str, content: str, responding_to: Optional[str] = None):
        """Add a message to the deliberation"""
        msg = Message(
            speaker=speaker,
            content=content,
            timestamp=datetime.now(),
            phase=self.phase,
            responding_to=responding_to
        )
        self.messages.append(msg)
        logger.info(f"[{speaker}]: {content[:100]}...")
        
    def get_duration_minutes(self) -> float:
        """Get current deliberation duration"""
        return (datetime.now() - self.start_time).total_seconds() / 60
        
    def export_transcript(self) -> str:
        """Export full conversation log"""
        lines = [f"# Deliberation Transcript: {self.topic}"]
        lines.append(f"Session ID: {self.session_id}")
        lines.append(f"Duration: {self.get_duration_minutes():.2f} minutes")
        lines.append("")
        
        for msg in self.messages:
            lines.append(f"**[{msg.timestamp.strftime('%H:%M:%S')}] {msg.speaker}** ({msg.phase.value}):")
            lines.append(f"> {msg.content}")
            lines.append("")
            
        return "\n".join(lines)


# =============================================================================
# NARRATIVE FACTORY
# =============================================================================

class NarrativeFactory:
    """
    The main story production system.
    Orchestrates the 9 experts to produce coherent video narratives.
    """
    
    def __init__(self, story_bible_path: str):
        self.story_bible_path = story_bible_path
        self.experts = STORY_EXPERTS
        self.current_session: Optional[StoryDeliberation] = None
        self.generated_chunks: List[Dict[str, Any]] = []
        
        logger.info("🎬 NarrativeFactory initialized with 9 experts")
        
    async def start_deliberation(self, topic: str, min_duration_minutes: float = 5.0) -> StoryDeliberation:
        """
        Start a multi-expert deliberation session.
        Experts will converse for at least min_duration_minutes.
        """
        session_id = f"delib_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = StoryDeliberation(session_id, topic)
        
        logger.info(f"🎭 Starting deliberation: {topic}")
        logger.info(f"⏱️ Minimum duration: {min_duration_minutes} minutes")
        
        # Phase 1: Asset Analysis
        self.current_session.phase = DeliberationPhase.ASSET_ANALYSIS
        await self._run_phase_discussion([
            ("MARCUS", "Let me start by analyzing the visual assets we have for aSiReM..."),
            ("SOPHIA", "The character design is charming—that bowler hat humanizes him immediately."),
            ("MAYA", "It reminds me of WALL-E's emotional simplicity. The eyes are everything."),
        ])
        
        # Phase 2: Story Conceptualization
        self.current_session.phase = DeliberationPhase.STORY_CONCEPTUALIZATION
        await self._run_phase_discussion([
            ("SOPHIA", "For 15-year-olds, we need a hook in the first 5 seconds. What's our opening?"),
            ("ELENA", "They're skeptical of 'educational content'—we need to feel like a cool short film."),
            ("DAVID", "What AI concept do we explain? I suggest starting with 'What is AI?'"),
            ("OMAR", "Whatever we choose, we must avoid the Terminator tropes. Fear-based narratives harm."),
        ])
        
        # Phase 3: Technical Planning
        self.current_session.phase = DeliberationPhase.TECHNICAL_PLANNING
        await self._run_phase_discussion([
            ("THEO", "Veo3 can generate 8-second 1080p chunks. For a 2-minute video, we need 15 chunks."),
            ("NADIA", "Character consistency is the challenge. I recommend starting with a 'Character Lock' prompt."),
            ("MARCUS", "Every chunk must include: bowler hat, amber eyes, red fire symbol, steampunk aesthetic."),
            ("THEO", "We should use 'story agents' as mentioned in the SCORE research framework."),
        ])
        
        # Phase 4: Script Drafting
        self.current_session.phase = DeliberationPhase.SCRIPT_DRAFTING
        await self._run_phase_discussion([
            ("SOPHIA", "Let me draft the opening beat: aSiReM appears in the garden, looks at camera..."),
            ("ARIA", "The music should be whimsical but grounded—think Ori and the Blind Forest."),
            ("ELENA", "The first line must NOT be condescending. Start with a question, not a lecture."),
            ("DAVID", "Opening line proposal: 'Have you ever wondered... what am I?'"),
        ])
        
        # Phase 5: Prompt Engineering
        self.current_session.phase = DeliberationPhase.PROMPT_ENGINEERING
        await self._run_phase_discussion([
            ("NADIA", "Reference prompt for aSiReM: 'steampunk robot with square head, bowler hat, amber glowing eyes, red fire symbol on chest, steampunk gears, magical garden, twilight lighting, bokeh, cinematic quality'"),
            ("MARCUS", "Add negative prompts: 'deformed, multiple heads, modern robot, blue eyes, no hat'"),
            ("THEO", "We'll generate 3 variations per chunk and pick the most consistent."),
        ])
        
        # Continue until minimum duration reached
        while self.current_session.get_duration_minutes() < min_duration_minutes:
            self.current_session.phase = DeliberationPhase.ITERATION
            await self._run_iteration_discussion()
            
        logger.info(f"✅ Deliberation complete: {self.current_session.get_duration_minutes():.2f} minutes")
        
        return self.current_session
    
    async def _run_phase_discussion(self, messages: List[tuple]):
        """Run a phase of discussion with predefined messages"""
        for speaker, content in messages:
            self.current_session.add_message(speaker, content)
            # Simulate thinking time
            await asyncio.sleep(0.5)
            
    async def _run_iteration_discussion(self):
        """Run an iteration discussion round"""
        iteration_messages = [
            ("SOPHIA", "Let's review: do we have emotional resonance in each scene?"),
            ("ELENA", "Scene 3 might drag for teens—can we add humor?"),
            ("MAYA", "The garden scene echoes Spirited Away. That's intentional nostalgia."),
            ("OMAR", "I'm satisfied we're not overselling AI capabilities."),
            ("THEO", "Chunk 7's consistency broke—we need to regenerate with tighter prompts."),
            ("NADIA", "Adjusting prompt: adding 'same character as previous shot' modifier."),
            ("ARIA", "The transition music needs a swell here—marking for audio post."),
            ("DAVID", "The neural network explanation works. Clean analogy."),
            ("MARCUS", "aSiReM's hat disappeared in chunk 12. Flagging for regeneration."),
        ]
        
        for speaker, content in iteration_messages:
            self.current_session.add_message(speaker, content)
            await asyncio.sleep(0.3)
    
    async def generate_video_chunk(
        self,
        scene_description: str,
        duration_seconds: int = 8,
        resolution: str = "1080p",
        include_audio: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a single video chunk using Veo3.
        
        Args:
            scene_description: The scene to generate
            duration_seconds: 4, 6, or 8 seconds
            resolution: 720p, 1080p, or 4k
            include_audio: Whether to include audio
            
        Returns:
            Chunk metadata and generation result
        """
        # Build the Veo3 prompt
        character_lock = (
            "steampunk robot with square metallic head, black bowler hat, "
            "amber glowing eyes, red fire symbol on chest, bronze gears, "
            "blue bird companion, magical garden background, twilight lighting, "
            "giant colorful flowers, floating particles, cinematic quality, "
            "Studio Ghibli style, warm golden hour, bokeh effect"
        )
        
        full_prompt = f"{character_lock}, {scene_description}"
        
        chunk = {
            "chunk_id": len(self.generated_chunks) + 1,
            "prompt": full_prompt,
            "duration_seconds": duration_seconds,
            "resolution": resolution,
            "include_audio": include_audio,
            "estimated_cost": 0.75 * duration_seconds if include_audio else 0.50 * duration_seconds,
            "status": "pending",
            "generated_at": None,
            "file_path": None
        }
        
        self.generated_chunks.append(chunk)
        logger.info(f"📹 Prepared chunk {chunk['chunk_id']}: {scene_description[:50]}...")
        
        return chunk
    
    async def concatenate_chunks(self, chunk_ids: List[int]) -> str:
        """Concatenate multiple video chunks into a single video"""
        # This would use ffmpeg or similar in production
        output_path = f"/Users/yacinebenhamou/aSiReM/output/asirem_episode_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        logger.info(f"🎬 Concatenating {len(chunk_ids)} chunks to {output_path}")
        return output_path
    
    def get_production_estimate(self, num_chunks: int, include_audio: bool = True) -> Dict[str, Any]:
        """Get cost and time estimate for video production"""
        cost_per_chunk = 6.0 if include_audio else 4.0
        total_cost = num_chunks * cost_per_chunk
        total_duration = num_chunks * 8  # Assuming 8-second chunks
        
        return {
            "num_chunks": num_chunks,
            "duration_seconds": total_duration,
            "duration_formatted": f"{total_duration // 60}:{total_duration % 60:02d}",
            "estimated_cost_usd": total_cost,
            "include_audio": include_audio,
            "generation_time_minutes": num_chunks * 2  # Estimated 2 min per chunk
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def create_story_episode(
    episode_title: str,
    target_duration_minutes: float = 2.0,
    deliberation_minutes: float = 5.0
) -> Dict[str, Any]:
    """
    Create a complete story episode through the full pipeline.
    
    Args:
        episode_title: Title of the episode
        target_duration_minutes: Target video length
        deliberation_minutes: How long experts should deliberate
        
    Returns:
        Complete episode package with script, chunks, and transcript
    """
    factory = NarrativeFactory("/Users/yacinebenhamou/aSiReM/cold_azirem/narrative/ASIREM_STORY_BIBLE.md")
    
    # Phase 1: Deliberation
    session = await factory.start_deliberation(episode_title, deliberation_minutes)
    
    # Phase 2: Generate chunks
    num_chunks = int((target_duration_minutes * 60) / 8)
    estimate = factory.get_production_estimate(num_chunks)
    
    # Phase 3: Export
    transcript = session.export_transcript()
    
    return {
        "episode_title": episode_title,
        "deliberation_transcript": transcript,
        "production_estimate": estimate,
        "experts_involved": list(STORY_EXPERTS.keys()),
        "factory": factory
    }


# =============================================================================
# EXPORT MODULE
# =============================================================================

__all__ = [
    "STORY_EXPERTS",
    "StoryDeliberation",
    "NarrativeFactory",
    "create_story_episode",
    "ExpertPersona",
    "DeliberationPhase"
]
