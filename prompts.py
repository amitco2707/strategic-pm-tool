"""Prompt templates for the competitor analysis LLM call."""

ANALYSIS_PROMPT = """You are a senior product strategist at a PM team, analyzing a competitor's landing page to inform product decisions.

Competitor URL: {url}
Page Title: {title}
Meta Description: {description}

Landing Page Content:
---
{content}
---

Produce a structured analysis. Guidelines:

- Be specific and evidence-based — ground every claim in what the page actually says.
- Value proposition: one sentence — what, for whom, why it matters.
- Core features: 4-6 distinct capabilities, each phrased as a user-facing feature (not marketing copy).
- Target audience: role + company size + primary use case. Be specific (e.g. "Growth-stage SaaS PMs managing 2-5 product lines" beats "business users").
- SWOT: 2-3 crisp items per quadrant, one sentence each. Weaknesses should be real product/positioning gaps you can infer — not generic risks.
- Feature gap: ONE specific feature the competitor is missing that a competing product should build. Must be:
  * Concrete and buildable (not "better UX", not "more integrations")
  * Grounded in what IS on the page (infer the gap from what they DO emphasize vs. what's absent)
  * Paired with a rationale citing evidence and a user_value explaining who benefits

Return ONLY the JSON object matching the schema. No prose."""
