import json
from pathlib import Path

from models import IssueFinding, ReviewOutput
from providers.base import ReviewProvider
from config import RESULTS_DIR


class FlatFileProvider(ReviewProvider):
    """Reads pre-existing review JSON files for manual providers."""

    def __init__(self, name: str, display_name: str | None = None):
        self.name = name
        self.display_name = display_name or name

    async def review_paper(self, paper_id: int, paper_text: str, prompt: str) -> ReviewOutput:
        path = self.result_path(paper_id)
        if not path.exists():
            raise FileNotFoundError(f"No result file at {path}")

        data = json.loads(path.read_text(encoding="utf-8"))

        # Accept either full ReviewOutput format or just {"issues": [...]}
        if "issues" in data and "provider_name" not in data:
            issues = [IssueFinding(**item) for item in data["issues"]]
            return ReviewOutput(
                paper_id=paper_id,
                provider_name=self.name,
                issues=issues,
                raw_response=json.dumps(data),
            )

        return ReviewOutput(**data)
