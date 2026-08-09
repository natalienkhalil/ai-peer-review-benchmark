import json
import re

import openai

from models import IssueFinding, ReviewOutput
from providers.base import ReviewProvider


class OpenAIProvider(ReviewProvider):
    def __init__(self, name: str, display_name: str, model: str,
                 reasoning_effort: str | None = None):
        self.name = name
        self.display_name = display_name
        self.model = model
        self.reasoning_effort = reasoning_effort

    async def review_paper(self, paper_id: int, paper_text: str, prompt: str) -> ReviewOutput:
        client = openai.AsyncOpenAI()
        filled_prompt = prompt.replace("{paper_text}", paper_text)

        kwargs: dict = {
            "model": self.model,
            "messages": [{"role": "user", "content": filled_prompt}],
        }

        if self.reasoning_effort and self.reasoning_effort != "none":
            kwargs["reasoning_effort"] = self.reasoning_effort
        else:
            kwargs["reasoning_effort"] = "none"
            kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**kwargs)
        raw_text = response.choices[0].message.content or ""

        issues = _parse_issues(raw_text)
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
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
        items = data.get("issues", data if isinstance(data, list) else [])
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


def make_openai_providers() -> list[OpenAIProvider]:
    return [
        OpenAIProvider("openai_gpt54_no_reasoning", "GPT-5.4 (No Reasoning)", "gpt-5.4", reasoning_effort="none"),
        OpenAIProvider("openai_gpt54_high_reasoning", "GPT-5.4 (High Reasoning)", "gpt-5.4", reasoning_effort="high"),
        OpenAIProvider("openai_gpt55_no_reasoning", "GPT-5.5 (No Reasoning)", "gpt-5.5", reasoning_effort="none"),
        OpenAIProvider("openai_gpt55_high_reasoning", "GPT-5.5 (High Reasoning)", "gpt-5.5", reasoning_effort="high"),
    ]
