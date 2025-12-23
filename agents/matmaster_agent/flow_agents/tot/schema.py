from pydantic import BaseModel, Field


class ThoughtEvaluationSchema(BaseModel):
    score: int = Field(..., description='Overall quality score (0-100)')
    keep: bool = Field(..., description='Whether to keep this branch in the beam')
    reasons: list[str] = Field(default_factory=list, description='Why this score was assigned')
    risks: list[str] = Field(default_factory=list, description='Potential failure points')
