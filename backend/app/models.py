from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SourceType(str, Enum):
    TEXT = "text"
    URL = "url"
    FILE = "file"

class ProcessRequest(BaseModel):
    source_type: SourceType
    content: str
    file_name: Optional[str] = None

class FactSheet(BaseModel):
    product_name: str
    features: List[str]
    specifications: Dict[str, Any]
    target_audience: str
    value_proposition: str
    ambiguous_statements: List[str] = []
    raw_data: Dict[str, Any] = {}

class CopywriterOutput(BaseModel):
    blog_post: str
    social_media_thread: List[str]
    email_teaser: str
    metadata: Dict[str, Any] = {}

class EditorFeedback(BaseModel):
    has_errors: bool
    hallucinations: List[str] = []
    tone_issues: List[str] = []
    factual_errors: List[str] = []
    suggestions: List[str] = []
    approved: bool = False

class AgentLog(BaseModel):
    agent_name: str
    status: str
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None

class PipelineResponse(BaseModel):
    success: bool
    fact_sheet: Optional[FactSheet] = None
    copywriter_output: Optional[CopywriterOutput] = None
    editor_feedback: Optional[EditorFeedback] = None
    logs: List[AgentLog] = []
    iterations: int = 0
    final_approved: bool = False
    error: Optional[str] = None