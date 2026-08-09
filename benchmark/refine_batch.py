#!/usr/bin/env python3
"""Kill-resilient two-phase Refine.ink runner.

Refine charges a credit at process-start and runs server-side for 8-17 min/paper.
A single long foreground job that gets killed mid-flight wastes those credits. So
we split the work:

  Phase 1 (submit): upload + start processing for every target paper, recording
    {document_id, history_id} to a state file (results/_refine_state.json).
  Phase 2 (poll):   GET /history/{history_id} for each pending paper until done,
    writing results incrementally.

Re-running resumes from the state file: already-submitted papers are never
re-submitted (no duplicate credit spend), already-finished papers are skipped.

Usage:
  uv run refine_batch.py                 # modified papers 1-10
  uv run refine_batch.py --originals     # original papers 1-10
"""

import argparse
import asyncio
import json
from pathlib import Path

import httpx
from dotenv import load_dotenv

from config import ENV_FILE, MODIFIED_PAPERS_DIR, ORIGINAL_PAPERS_DIR, RESULTS_DIR
from docx_extract import extract_text
from docx_to_pdf import text_to_pdf
from models import ReviewOutput
from providers.refine_provider import BASE, _comment_to_issue

STATE_PATH = RESULTS_DIR / "_refine_state.json"
import os
import tempfile


def load_state() -> dict:
    return json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}


def save_state(s: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(s, indent=2))


async def submit(client, key, pdf_path) -> tuple[str, str]:
    headers = {"Authorization": f"Bearer {key}"}
    with open(pdf_path, "rb") as fh:
        r = await client.post(f"{BASE}/documents/upload", headers=headers,
                              files={"file": (pdf_path.name, fh, "application/pdf")})
    r.raise_for_status()
    task_id = r.json()["task_id"]

    document_id = None
    async with client.stream("GET", f"{BASE}/documents/upload/events/{task_id}?token={key}") as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
            if not line.startswith("data:"):
                continue
            try:
                data = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
            res = data.get("result") if isinstance(data, dict) else None
            if isinstance(res, dict) and res.get("document_id"):
                document_id = res["document_id"]
                break
    if not document_id:
        raise RuntimeError("no document_id from upload SSE")

    r = await client.post(f"{BASE}/documents/{document_id}/process", headers=headers,
                          json={"preview": False})
    r.raise_for_status()
    return document_id, r.json()["history_id"]


def finalize(data: dict, pid: int, name: str) -> ReviewOutput:
    fb = data.get("feedback") or {}
    det = fb.get("detailed") or {}
    comments = det.get("comments") or []
    overall = (fb.get("overall") or {}).get("content", "")
    return ReviewOutput(
        paper_id=pid, provider_name=name,
        issues=[_comment_to_issue(c) for c in comments],
        raw_response=json.dumps({"overall": overall, "comments": comments}),
        model_id="refine.ink",
    )


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--originals", action="store_true")
    ap.add_argument("--papers")
    ap.add_argument("--submit-only", action="store_true")
    args = ap.parse_args()
    load_dotenv(ENV_FILE)
    key = os.environ["REFINE_API_KEY"]

    name = "refine_ink_originals" if args.originals else "refine_ink"
    paper_dir = ORIGINAL_PAPERS_DIR if args.originals else MODIFIED_PAPERS_DIR
    rdir = RESULTS_DIR / name
    rdir.mkdir(parents=True, exist_ok=True)
    ids = [int(x) for x in args.papers.split(",")] if args.papers else list(range(1, 11))

    def rpath(pid): return rdir / f"paper_{pid}_review.json"

    state = load_state()
    timeout = httpx.Timeout(60.0, read=120.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Phase 1: submit any paper lacking a result and a state entry
        async def ensure_submitted(pid):
            skey = f"{name}:{pid}"
            if rpath(pid).exists() or skey in state:
                return
            tmp = Path(tempfile.mkdtemp()) / f"paper_{pid}.pdf"
            text_to_pdf(extract_text(paper_dir / f"{pid}.docx"), tmp)
            doc, hist = await submit(client, key, tmp)
            state[skey] = {"document_id": doc, "history_id": hist}
            save_state(state)
            print(f"  submitted paper {pid}: history_id={hist}")

        await asyncio.gather(*(ensure_submitted(pid) for pid in ids))
        if args.submit_only:
            print(f"{name}: submitted all (poll later)")
            return

        # Phase 2: poll pending papers until each completes
        headers = {"Authorization": f"Bearer {key}"}
        pending = [pid for pid in ids if not rpath(pid).exists()]
        waited = 0
        while pending:
            for pid in list(pending):
                hist = state[f"{name}:{pid}"]["history_id"]
                r = await client.get(f"{BASE}/history/{hist}", headers=headers)
                r.raise_for_status()
                data = r.json()
                comments = ((data.get("feedback") or {}).get("detailed") or {}).get("comments")
                if not data.get("is_processing", False) and comments is not None:
                    out = finalize(data, pid, name)
                    rpath(pid).write_text(out.model_dump_json(indent=2), encoding="utf-8")
                    print(f"  DONE paper {pid}: {len(out.issues)} issues")
                    pending.remove(pid)
            if pending:
                if waited > 2400:
                    print(f"  timeout; still pending: {pending}")
                    break
                await asyncio.sleep(20)
                waited += 20
    print(f"{name}: complete ({sum(rpath(p).exists() for p in ids)}/{len(ids)})")


if __name__ == "__main__":
    asyncio.run(main())
