"""Provider for Reviewer3 (commercial reviewer): submits a rendered PDF and polls
until the review completes. Requires REVIEWER3_API_KEY and REVIEWER3_USER_ID in .env.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import httpx

from docx_to_pdf import text_to_pdf
from models import IssueFinding, ReviewOutput
from providers.base import ReviewProvider

BASE = "https://reviewer3.com"

_SEVERITY = {1: "critical", 2: "major", 3: "minor", 4: "editorial"}


class Reviewer3Provider(ReviewProvider):
    def __init__(self, name: str = "reviewer3", display_name: str = "Reviewer3",
                 review_mode: str = "journal"):
        self.name = name
        self.display_name = display_name
        self.review_mode = review_mode

    async def review_paper(self, paper_id: int, paper_text: str, prompt: str) -> ReviewOutput:
        key = os.environ["REVIEWER3_API_KEY"]
        user_id = os.environ.get("REVIEWER3_USER_ID")
        if not user_id:
            raise RuntimeError("REVIEWER3_USER_ID env var is required (review submission needs a userId)")
        headers = {"x-api-key": key}

        tmp = Path(tempfile.mkdtemp()) / f"paper_{paper_id}.pdf"
        text_to_pdf(paper_text, tmp)

        timeout = httpx.Timeout(120.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # 1. submit (fire-and-forget)
            with open(tmp, "rb") as fh:
                r = await client.post(
                    f"{BASE}/api/internal/review",
                    headers=headers,
                    files={"file": (tmp.name, fh, "application/pdf")},
                    data={
                        "userId": user_id,
                        "filename": f"paper_{paper_id}.pdf",
                        "title": f"Benchmark Paper {paper_id}",
                        "reviewMode": self.review_mode,
                        "sendEmail": "false",
                    },
                )
            if r.status_code != 200:
                raise RuntimeError(f"submit failed {r.status_code}: {r.text[:300]}")
            session_id = r.json()["sessionId"]

            # 2. poll until completed
            session = await self._poll(client, headers, session_id)

        status = session.get("status")
        comments = session.get("comments") or []
        issues = [_comment_to_issue(c) for c in comments]
        return ReviewOutput(
            paper_id=paper_id,
            provider_name=self.name,
            issues=issues,
            raw_response=json.dumps(session),
            model_id=f"reviewer3:{self.review_mode}",
            token_usage={"session_id": session_id, "status": status},
        )

    async def _poll(self, client, headers, session_id, max_wait=1800, interval=15) -> dict:
        waited = 0
        while True:
            r = await client.get(f"{BASE}/api/internal/review/{session_id}", headers=headers)
            r.raise_for_status()
            data = r.json()
            status = data.get("status")
            if status in ("completed", "error"):
                return data
            if waited >= max_wait:
                data["status"] = data.get("status") or "timeout"
                return data
            await asyncio.sleep(interval)
            waited += interval


def _comment_to_issue(c: dict) -> IssueFinding:
    title = c.get("title", "") or ""
    body = c.get("comment", "") or ""
    description = f"{title}: {body}".strip(": ").strip() if title else body
    sev = c.get("severity")
    return IssueFinding(
        category="reviewer3",
        subcategory=title or (c.get("reviewerId") or None),
        description=description or "(no comment)",
        quote=c.get("citedText") or "",
        location=None,
        severity=_SEVERITY.get(sev, str(sev) if sev is not None else None),
    )


def make_reviewer3_providers() -> list[Reviewer3Provider]:
    mode = os.environ.get("REVIEWER3_MODE", "journal")
    return [Reviewer3Provider(review_mode=mode)]
