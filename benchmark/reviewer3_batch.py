#!/usr/bin/env python3
"""Kill-resilient two-phase Reviewer3 runner (mirrors refine_batch.py).

Reviewer3's POST /review is fire-and-forget (returns a sessionId immediately),
then the review runs server-side for minutes (journal mode = 6+ reviewers). We
submit every target paper first (recording sessionId -> state), then poll. Re-runs
resume from state without re-submitting.

Usage:
  uv run reviewer3_batch.py                 # modified papers 1-10
  uv run reviewer3_batch.py --originals     # original papers 1-10
  uv run reviewer3_batch.py --submit-only   # just fire submissions
"""

import argparse
import asyncio
import json
import os
import tempfile
from pathlib import Path

import httpx
from dotenv import load_dotenv

from config import ENV_FILE, MODIFIED_PAPERS_DIR, ORIGINAL_PAPERS_DIR, RESULTS_DIR
from docx_extract import extract_text
from docx_to_pdf import text_to_pdf
from models import ReviewOutput
from providers.reviewer3_provider import BASE, _comment_to_issue

STATE_PATH = RESULTS_DIR / "_reviewer3_state.json"


def load_state() -> dict:
    return json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}


def save_state(s: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(s, indent=2))


async def submit(client, key, user_id, mode, pid, pdf_path) -> str:
    with open(pdf_path, "rb") as fh:
        r = await client.post(
            f"{BASE}/api/internal/review",
            headers={"x-api-key": key},
            files={"file": (pdf_path.name, fh, "application/pdf")},
            data={"userId": user_id, "filename": f"paper_{pid}.pdf",
                  "title": f"Benchmark Paper {pid}", "reviewMode": mode, "sendEmail": "false"},
        )
    if r.status_code != 200:
        raise RuntimeError(f"submit failed {r.status_code}: {r.text[:200]}")
    return r.json()["sessionId"]


def finalize(data: dict, pid: int, name: str, mode: str) -> ReviewOutput:
    comments = data.get("comments") or []
    return ReviewOutput(
        paper_id=pid, provider_name=name,
        issues=[_comment_to_issue(c) for c in comments],
        raw_response=json.dumps(data), model_id=f"reviewer3:{mode}",
        token_usage={"session_id": (data.get("session") or {}).get("id"), "status": data.get("status")},
    )


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--originals", action="store_true")
    ap.add_argument("--papers")
    ap.add_argument("--submit-only", action="store_true")
    args = ap.parse_args()
    load_dotenv(ENV_FILE)
    key = os.environ["REVIEWER3_API_KEY"]
    user_id = os.environ["REVIEWER3_USER_ID"]
    mode = os.environ.get("REVIEWER3_MODE", "journal")

    name = "reviewer3_originals" if args.originals else "reviewer3"
    paper_dir = ORIGINAL_PAPERS_DIR if args.originals else MODIFIED_PAPERS_DIR
    rdir = RESULTS_DIR / name
    rdir.mkdir(parents=True, exist_ok=True)
    ids = [int(x) for x in args.papers.split(",")] if args.papers else list(range(1, 11))

    def rpath(pid): return rdir / f"paper_{pid}_review.json"

    state = load_state()
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        async def ensure_submitted(pid):
            skey = f"{name}:{pid}"
            if rpath(pid).exists() or skey in state:
                return
            tmp = Path(tempfile.mkdtemp()) / f"paper_{pid}.pdf"
            text_to_pdf(extract_text(paper_dir / f"{pid}.docx"), tmp)
            sid = await submit(client, key, user_id, mode, pid, tmp)
            state[skey] = {"session_id": sid}
            save_state(state)
            print(f"  submitted paper {pid}: session={sid}")

        await asyncio.gather(*(ensure_submitted(pid) for pid in ids))
        if args.submit_only:
            print(f"{name}: submitted all (poll later)")
            return

        headers = {"x-api-key": key}
        pending = [pid for pid in ids if not rpath(pid).exists()]
        waited = 0
        while pending:
            for pid in list(pending):
                sid = state[f"{name}:{pid}"]["session_id"]
                r = await client.get(f"{BASE}/api/internal/review/{sid}", headers=headers)
                r.raise_for_status()
                data = r.json()
                if data.get("status") in ("completed", "error"):
                    out = finalize(data, pid, name, mode)
                    rpath(pid).write_text(out.model_dump_json(indent=2), encoding="utf-8")
                    print(f"  DONE paper {pid}: {len(out.issues)} issues ({data.get('status')})")
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
