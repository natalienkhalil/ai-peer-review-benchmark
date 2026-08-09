from abc import ABC, abstractmethod
from pathlib import Path
from models import ReviewOutput
from config import RESULTS_DIR


class ReviewProvider(ABC):
    name: str
    display_name: str

    @abstractmethod
    async def review_paper(self, paper_id: int, paper_text: str, prompt: str) -> ReviewOutput:
        ...

    def result_dir(self) -> Path:
        d = RESULTS_DIR / self.name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def result_path(self, paper_id: int) -> Path:
        return self.result_dir() / f"paper_{paper_id}_review.json"

    def has_result(self, paper_id: int) -> bool:
        return self.result_path(paper_id).exists()
