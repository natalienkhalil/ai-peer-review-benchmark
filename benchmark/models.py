from pydantic import BaseModel


class IssueFinding(BaseModel):
    category: str
    subcategory: str | None = None
    description: str
    quote: str = ""
    location: str | None = None
    severity: str | None = None


class ReviewOutput(BaseModel):
    paper_id: int
    provider_name: str
    issues: list[IssueFinding]
    raw_response: str | None = None
    model_id: str | None = None
    token_usage: dict | None = None


class GroundTruthError(BaseModel):
    paper: int
    category: str
    subcategory: str
    difficulty: int
    difficulty_rationale: str
    original_snippet: str
    modified_snippet: str
    description: str


class MatchResult(BaseModel):
    ground_truth: GroundTruthError
    matched: bool
    match_confidence: float = 0.0
    matched_finding: IssueFinding | None = None
    match_method: str | None = None


class PaperScore(BaseModel):
    paper_id: int
    provider_name: str
    errors_detected: int
    errors_missed: int
    total_findings: int
    matches: list[MatchResult]
