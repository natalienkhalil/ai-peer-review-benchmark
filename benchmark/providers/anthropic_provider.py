import json
import re
from datetime import datetime, timezone

import anthropic

from models import IssueFinding, ReviewOutput
from providers.base import ReviewProvider


class AnthropicProvider(ReviewProvider):
    def __init__(self, name: str, display_name: str, model: str,
                 thinking_budget: int | None = None):
        self.name = name
        self.display_name = display_name
        self.model = model
        self.thinking_budget = thinking_budget

    async def review_paper(self, paper_id: int, paper_text: str, prompt: str) -> ReviewOutput:
        client = anthropic.AsyncAnthropic()
        filled_prompt = prompt.replace("{paper_text}", paper_text)

        kwargs: dict = {
            "model": self.model,
            "max_tokens": 16384,
            "messages": [{"role": "user", "content": filled_prompt}],
        }

        # Opus 4.8+ deprecated `temperature` and replaced budget-based extended
        # thinking ("thinking.type.enabled") with adaptive thinking
        # ("thinking.type.adaptive" + "output_config.effort").
        is_new_api = "4-8" in self.model
        want_thinking = self.thinking_budget is not None and self.thinking_budget > 0

        if is_new_api:
            if want_thinking:
                kwargs["thinking"] = {"type": "adaptive"}
                kwargs["output_config"] = {"effort": "high"}
                kwargs["max_tokens"] = max(16384, self.thinking_budget + 8192)
            # no-thinking on the new API: leave default effort, no temperature.
        elif want_thinking:
            kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.thinking_budget,
            }
            kwargs["max_tokens"] = max(16384, self.thinking_budget + 8192)
            kwargs["temperature"] = 1  # required when thinking is enabled
        else:
            kwargs["temperature"] = 0

        # Use streaming to avoid 10-minute timeout on long thinking requests
        raw_text = ""
        input_tokens = 0
        output_tokens = 0

        async with client.messages.stream(**kwargs) as stream:
            response = await stream.get_final_message()

        for block in response.content:
            if block.type == "text":
                raw_text += block.text

        issues = _parse_issues(raw_text)
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
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
    """Parse JSON issues from model response, handling various formats."""
    candidates = [text]

    # Extract from markdown code fences
    for pattern in [r"```json\s*\n(.*?)\n\s*```", r"```\s*\n(.*?)\n\s*```"]:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            candidates.insert(0, match.group(1))

    # Try each candidate
    for candidate in candidates:
        # Try direct parse
        try:
            data = json.loads(candidate)
            items = data.get("issues", data if isinstance(data, list) else [])
            return [IssueFinding(**item) for item in items]
        except (json.JSONDecodeError, Exception):
            pass

        # Try fixing common JSON issues: unescaped quotes in strings
        try:
            # Find the outermost { ... } containing "issues"
            brace_match = re.search(r'\{[\s\S]*"issues"[\s\S]*\}', candidate)
            if brace_match:
                data = json.loads(brace_match.group(0))
                items = data.get("issues", [])
                return [IssueFinding(**item) for item in items]
        except (json.JSONDecodeError, Exception):
            pass

        # Last resort: extract individual issue objects via regex
        try:
            issue_pattern = r'\{[^{}]*"category"\s*:\s*"[^"]*"[^{}]*"description"\s*:\s*"[^"]*"[^{}]*\}'
            found = re.findall(issue_pattern, candidate)
            if found:
                items = []
                for obj_str in found:
                    try:
                        items.append(IssueFinding(**json.loads(obj_str)))
                    except Exception:
                        continue
                if items:
                    return items
        except Exception:
            pass

    return []


def make_anthropic_providers() -> list[AnthropicProvider]:
    return [
        AnthropicProvider("claude_sonnet_no_thinking", "Claude Sonnet 4.6 (No Thinking)", "claude-sonnet-4-6", thinking_budget=None),
        AnthropicProvider("claude_sonnet_high_thinking", "Claude Sonnet 4.6 (High Thinking)", "claude-sonnet-4-6", thinking_budget=50000),
        AnthropicProvider("claude_opus_no_thinking", "Claude Opus 4.6 (No Thinking)", "claude-opus-4-6", thinking_budget=None),
        AnthropicProvider("claude_opus_high_thinking", "Claude Opus 4.6 (High Thinking)", "claude-opus-4-6", thinking_budget=50000),
        # Newer versions (added 2026-06-24). Note: Sonnet 4.8 is not yet available
        # on the API (latest Sonnet is 4-6), so only Opus is bumped to 4.8 here.
        AnthropicProvider("claude_opus48_no_thinking", "Claude Opus 4.8 (No Thinking)", "claude-opus-4-8", thinking_budget=None),
        AnthropicProvider("claude_opus48_high_thinking", "Claude Opus 4.8 (High Thinking)", "claude-opus-4-8", thinking_budget=50000),
    ]
