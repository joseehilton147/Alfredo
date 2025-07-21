"""
Entidades de domínio do Alfredo AI.

Este módulo exporta todas as entidades de domínio que representam
os conceitos centrais do negócio.
"""

from .video import Video
from .audio_track import AudioTrack
from .transcription import Transcription, TranscriptionSegment
from .summary import Summary, SummarySection

__all__ = [
    "Video",
    "AudioTrack", 
    "Transcription",
    "TranscriptionSegment",
    "Summary",
    "SummarySection",
]