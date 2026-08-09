"""Refine.ink provider.

Flow (https://api.refine.ink, Bearer auth):
  1. POST /documents/upload (multipart file)            -> task_id
  2. GET  /documents/upload/events/{task_id} (SSE)      -> document_id
  3. POST /documents/{document_id}/process {preview}    -> history_id  (1 paid credit)
  4. GET  /documents/{document_id}/process/events/{id}  -> wait complete (SSE)
  5. GET  /history/{history_id}                         -> feedback.detailed.comments[]

We upload a PDF rendered from the same extract_text() the LLM providers receive,
so all systems under benchmark see identical manuscript content.
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

BASE = "https://api.refine.ink"


class RefineProvider(ReviewProvider):
    def __init__(self, name: str = "refine_ink", display_name: str = "Refine.ink"):
        self.name = name
        self.display_name = display_name

    async def review_paper(self, paper_id: int, paper_text: str, prompt: str) -> ReviewOutput:
        key = os.environ["REFINE_API_KEY"]
        headers = {"Authorization": f"Bearer {key}"}

        tmp = Path(tempfile.mkdtemp()) / f"paper_{paper_id}.pdf"
        text_to_pdf(paper_text, tmp)

        timeout = httpx.Timeout(60.0, read=900.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # 1. upload
            with open(tmp, "rb") as fh:
                r = await client.post(
                    f"{BASE}/documents/upload",
                    headers=headers,
                    files={"file": (tmp.name, fh, "application/pdf")},
                )
            r.raise_for_status()
            task_id = r.json()["task_id"]

            # 2. upload SSE -> document_id
            document_id = await self._sse_value(
                client, f"{BASE}/documents/upload/events/{task_id}?token={key}", "document_id"
            )
            if not document_id:
                raise RuntimeError("upload SSE did not yield a document_id")

            # 3. process
            r = await client.post(
                f"{BASE}/documents/{document_id}/process",
                headers=headers,
                json={"preview": False},
            )
            r.raise_for_status()
            history_id = r.json()["history_id"]

            # 4. processing SSE (best-effort; we poll /history as source of truth)
            try:
                await self._sse_drain(
                    client, f"{BASE}/documents/{document_id}/process/events/{history_id}?token={key}"
                )
            except Exception:
                pass

            # 5. poll /history for the finished feedback
            session = await self._poll_history(client, headers, history_id)

        feedback = (session.get("feedback") or {})
        detailed = (feedback.get("detailed") or {})
        comments = detailed.get("comments") or []
        overall = (feedback.get("overall") or {}).get("content", "")

        issues = [_comment_to_issue(c) for c in comments]
        return ReviewOutput(
            paper_id=paper_id,
            provider_name=self.name,
            issues=issues,
            raw_response=json.dumps({"overall": overall, "comments": comments}),
            model_id="refine.ink",
            token_usage={"document_id": document_id, "history_id": history_id},
        )

    async def _sse_value(self, client: httpx.AsyncClient, url: str, field: str) -> str | None:
        """Stream an SSE endpoint until a data payload contains `field`."""
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line[len("data:"):].strip()
                if not payload:
                    continue
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if isinstance(data, dict):
                    if data.get("error"):
                        raise RuntimeError(f"SSE error: {data['error']}")
                    if data.get(field):
                        return data[field]
                    result = data.get("result")
                    if isinstance(result, dict) and result.get(field):
                        return result[field]
        return None

    async def _sse_drain(self, client: httpx.AsyncClient, url: str) -> None:
        """Consume a processing SSE stream until it closes or signals completion."""
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line[len("data:"):].strip()
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if isinstance(data, dict):
                    status = str(data.get("status", "")).lower()
                    if data.get("error"):
                        raise RuntimeError(f"processing error: {data['error']}")
                    if status in ("complete", "completed", "done") or data.get("complete"):
                        return

    async def _poll_history(self, client, headers, history_id, max_wait=900, interval=8) -> dict:
        waited = 0
        while True:
            r = await client.get(f"{BASE}/history/{history_id}", headers=headers)
            r.raise_for_status()
            data = r.json()
            processing = data.get("is_processing", False)
            comments = (((data.get("feedback") or {}).get("detailed") or {}).get("comments"))
            if not processing and comments is not None:
                return data
            if waited >= max_wait:
                return data
            await asyncio.sleep(interval)
            waited += interval


def _comment_to_issue(c: dict) -> IssueFinding:
    title = c.get("title", "") or ""
    message = c.get("message", "") or ""
    description = f"{title}: {message}".strip(": ").strip() if title else message
    return IssueFinding(
        category="refine_feedback",
        subcategory=title or None,
        description=description or "(no message)",
        quote=c.get("quote") or c.get("paragraph") or "",
        location=None,
        severity=str(c.get("score")) if c.get("score") is not None else None,
    )


def make_refine_providers() -> list[RefineProvider]:
    return [RefineProvider()]
