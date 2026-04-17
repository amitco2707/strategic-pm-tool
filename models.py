"""Pydantic schemas for structured LLM output."""
from typing import List
from pydantic import BaseModel, Field


class SWOT(BaseModel):
    strengths: List[str] = Field(description="2-3 concise strengths, one sentence each")
    weaknesses: List[str] = Field(description="2-3 concise weaknesses, one sentence each")
    opportunities: List[str] = Field(description="2-3 market opportunities, one sentence each")
    threats: List[str] = Field(description="2-3 competitive or market threats, one sentence each")


class FeatureGap(BaseModel):
    gap: str = Field(description="One specific feature this competitor is missing")
    rationale: str = Field(description="Why this gap exists — what signals from the page support this")
    user_value: str = Field(description="Why users would care if someone built this")


class AnalysisResult(BaseModel):
    company_name: str
    value_proposition: str = Field(description="One-sentence core value prop")
    core_features: List[str] = Field(description="4-6 distinct product features highlighted on the page")
    target_audience: str = Field(description="Who they sell to — role, company size, use case")
    swot: SWOT
    feature_gap: FeatureGap
