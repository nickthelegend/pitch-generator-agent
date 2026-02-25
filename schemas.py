from __future__ import annotations

from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

LayoutType = Literal[
    'title',
    'content',
    'quote',
    'statistics',
    'timeline',
    'image',
    'comparison',
    'conclusion',
]


class BrandKit(BaseModel):
    name: Optional[str] = None
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None
    fontFamily: Optional[str] = None
    logoUrl: Optional[str] = None


class Slide(BaseModel):
    title: str
    layoutType: LayoutType = 'content'
    bullets: List[str] = Field(default_factory=list)
    speakerNotes: str = ''
    backgroundColor: str = '#0a0a0f'
    textColor: str = '#ffffff'
    accentColor: str = '#ec4899'
    gradient: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    icon: Optional[str] = None
    htmlContent: Optional[str] = None
    audioUrl: Optional[str] = None
    duration: Optional[float] = None


class GenerateSlidesRequest(BaseModel):
    topic: str
    count: int = 5
    style: str = 'Modern'


class GenerateSlidesResponse(BaseModel):
    slides: List[Slide]


class UpdateSlideRequest(BaseModel):
    topic: str
    instruction: str
    currentSlide: Slide
    style: str = 'Modern'


class UpdateSlideResponse(BaseModel):
    slide: Slide


class TTSLine(BaseModel):
    speaker: Optional[str] = None
    line: str


class TTSRequest(BaseModel):
    script: List[TTSLine]
    language: str = 'en-US'
    provider: Optional[str] = None
    voice: Optional[str] = None
    voiceMap: Optional[Dict[str, str]] = None


class TTSResponse(BaseModel):
    audio: str


class VideoRenderRequest(BaseModel):
    topic: str
    slides: List[Slide]
    format: Literal['16:9', '4:5', '9:16'] = '16:9'
    brand: Optional[BrandKit] = None
    fps: int = 30
    outputFormat: Literal['mp4', 'webm'] = 'mp4'
    generateAudio: bool = True
    ttsLanguage: str = 'en-US'
    ttsProvider: Optional[str] = None
    ttsVoice: Optional[str] = None


class VideoRenderResponse(BaseModel):
    videoPath: str
    videoFilename: str
    ipfsUrl: Optional[str] = None
    gatewayUrl: Optional[str] = None
    ipfsHash: Optional[str] = None
