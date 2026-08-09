import json
import re
import os

from google import genai

from models import IssueFinding, ReviewOutput
from providers.base import ReviewProvider


class GeminiProvider(ReviewProvider):
    def __init__(self, name: str, display_name: str, model: str):
        self.name = name
        self.display_name = display_name
        self.model = model

    async def review_paper(self, paper_id: int, paper_text: str, prompt: str) -> ReviewOutput:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        filled_prompt = prompt.replace("{paper_text}", paper_text)
        # Add instruction to be exhaustive — Gemini tends to stop at ~10 issues
        filled_prompt += "\n\nIMPORTANT: Be exhaustive. A typical manuscript has 20-40 identifiable issues. Do not stop at 10. List every issue you can find, no matter how minor."

        response = client.models.generate_content(
            model=self.model,
            contents=filled_prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=65536,
                response_mime_type="application/json",
            ),
        )

        raw_text = response.text or ""
        issues = _parse_issues(raw_text)

        usage = {}
        if response.usage_metadata:
            usage = {
                "input_tokens": response.usage_metadata.prompt_token_count,
                "output_tokens": response.usage_metadata.candidates_token_count,
            }

        return ReviewOutput(
            paper_id=paper_id,
            provider_name=self.name,
            issues=issues,
            raw_response=raw_text,
            model_id=self.model,
            token_usage=usage,
        )


def _parse_issues(text: str) -> list[IssueFinding]:
    try:
        data = json.loads(text)
        # Handle both {"issues": [...]} and bare [...]
        if isinstance(data, list):
            return [IssueFinding(**item) for item in data]
        items = data.get("issues", [])
        return [IssueFinding(**item) for item in items]
    except (json.JSONDecodeError, Exception):
        pass

    patterns = [
        r"```json\s*\n(.*?)\n\s*```",
        r"```\s*\n(.*?)\n\s*```",
        r"\{[\s\S]*\"issues\"[\s\S]*\}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1) if match.lastindex else match.group(0))
                items = data.get("issues", data if isinstance(data, list) else [])
                return [IssueFinding(**item) for item in items]
            except (json.JSONDecodeError, Exception):
                continue

    return []


def make_gemini_providers() -> list[GeminiProvider]:
    return [
        GeminiProvider("gemini_pro", "Gemini 3.1 Pro", "gemini-3.1-pro-preview"),
        GeminiProvider("gemini_flash", "Gemini 3 Flash", "gemini-3-flash-preview"),
    ]
