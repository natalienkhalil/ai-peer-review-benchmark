from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BENCHMARK_DIR = Path(__file__).resolve().parent
MODIFIED_PAPERS_DIR = PROJECT_ROOT / "modified papers"
ORIGINAL_PAPERS_DIR = PROJECT_ROOT / "original papers"
GROUND_TRUTH_CSV = PROJECT_ROOT / "error_insertions.csv"
RESULTS_DIR = BENCHMARK_DIR / "results"
REPORTS_DIR = BENCHMARK_DIR / "reports"
ENV_FILE = BENCHMARK_DIR / ".env"

MATCH_THRESHOLD = 0.35
