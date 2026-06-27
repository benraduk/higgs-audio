"""Batch multilingual smoke test for Higgs Audio v3 (local or cloud API)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from test_client import SAMPLES, synthesize
OUTPUT_DIR = SCRIPT_DIR / "output" / "multilingual"


def main() -> None:
    parser = argparse.ArgumentParser(description="Higgs Audio v3 multilingual batch test")
    parser.add_argument(
        "--url",
        default=os.environ.get("TTS_URL", "http://localhost:8000/v1/audio/speech"),
    )
    parser.add_argument("--auth", default=os.environ.get("BOSON_API_KEY"))
    parser.add_argument("--model", default=os.environ.get("TTS_MODEL"))
    parser.add_argument(
        "--languages",
        default="en,zh,ja,es,fr,de,ko,ar,hi,pt",
        help="Comma-separated language keys from built-in samples",
    )
    args = parser.parse_args()

    langs = [x.strip() for x in args.languages.split(",") if x.strip()]
    unknown = [l for l in langs if l not in SAMPLES]
    if unknown:
        print(f"Unknown language keys: {unknown}")
        print(f"Available: {', '.join(sorted(SAMPLES.keys()))}")
        sys.exit(1)

    print(f"Testing {len(langs)} languages against {args.url}")
    failures: list[str] = []

    for lang in langs:
        text = SAMPLES[lang]
        out = OUTPUT_DIR / f"{lang}.wav"
        print(f"[{lang}] {text[:50]}...")
        try:
            synthesize(args.url, text, out, args.auth, args.model)
        except requests.RequestException as exc:
            print(f"  FAILED: {exc}")
            failures.append(lang)

    if failures:
        print(f"\nFailed: {', '.join(failures)}")
        sys.exit(1)
    print(f"\nAll {len(langs)} languages OK. Files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
