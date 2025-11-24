from typing import TypedDict, List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class UserConfig(BaseModel):
    """Complete user request configuration"""
    topic: str = Field(..., description="Content topic")
    platform: str = Field(..., description="Target platform")
    avatar_id: str = Field(..., description="Avatar identifier")
    custom_avatar_params: Optional[Dict[str, Any]] = Field(None, description="Custom avatar parameters")
    additional_context: Optional[str] = Field(None, description="Extra context")
    target_audience: Optional[str] = Field(None, description="Audience targeting")


class ContextLayer(BaseModel):
    """Complete context for content generation"""
    persona_voice: str = Field("", description="Avatar voice characteristics")
    platform_rules: str = Field("", description="Platform-specific constraints")
    viral_dna: str = Field("", description="Content structure template")


class DraftArtifact(BaseModel):
    """Complete generated content artifact"""
    hook: str = Field("", description="Opening hook")
    re_hook: str = Field("", description="Secondary hook")
    body: str = Field("", description="Main content body")
    twist: str = Field("", description="Counter-intuitive conclusion")
    cta: str = Field("", description="Call to action")
    visuals: List[str] = Field(default_factory=list, description="Emojis")
    full_text: str = Field("", description="Complete assembled content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DiagnosticVector(BaseModel):
    """Complete performance and quality metrics"""
    compliance_score: float = Field(0.0, description="Rule compliance %")
    creative_score: float = Field(0.0, description="Creative quality 0-10")
    engagement_score: float = Field(0.0, description="Predicted engagement 0-10")
    flags: List[str] = Field(default_factory=list, description="Issues detected")
    attempt_count: int = Field(1, description="Iteration count")
    reasoning: str = Field("", description="Director's feedback")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra metrics")


class ContentState(TypedDict):
    """The Global State Object - Single Source of Truth"""
    request_id: str
    user_config: UserConfig
    context_layer: ContextLayer
    ground_truth: List[str]
    draft_artifact: DraftArtifact
    diagnostic_vector: DiagnosticVector
    loop_continue: bool
    final_output: Optional[str]


def create_initial_state(user_config: UserConfig) -> ContentState:
    """Initialize the state object"""
    return ContentState(
        request_id=str(uuid.uuid4()),
        user_config=user_config,
        context_layer=ContextLayer(),
        ground_truth=[],
        draft_artifact=DraftArtifact(),
        diagnostic_vector=DiagnosticVector(),
        loop_continue=True,
        final_output=None
    )