"""
aSiReM Avatar Module
Real-time interactive avatar system.
"""

from .engine import (
    AvatarEngine,
    AvatarConfig,
    MotionBackend,
    LipSyncBackend,
    VoiceBackend,
    RenderBackend,
    create_avatar_engine,
)

__all__ = [
    "AvatarEngine",
    "AvatarConfig",
    "MotionBackend",
    "LipSyncBackend",
    "VoiceBackend",
    "RenderBackend",
    "create_avatar_engine",
]
