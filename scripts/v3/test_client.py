"""Smoke test for Higgs Audio v3 TTS (local SGLang-Omni or Boson cloud API)."""

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
OUTPUT_DIR = SCRIPT_DIR / "output"

SAMPLES = {
    "en": "Hello! This is Higgs Audio v3 testing English speech synthesis.",
    "zh": "你好，这是 Higgs Audio v3 的中文语音合成测试。",
    "ja": "こんにちは。これは Higgs Audio v3 の日本語テストです。",
    "es": "Hola, esta es una prueba de síntesis de voz en español.",
    "fr": "Bonjour, ceci est un test de synthèse vocale en français.",
    "de": "Hallo, das ist ein deutscher Sprachsynthese-Test.",
    "ko": "안녕하세요. 히그스 오디오 v3 한국어 테스트입니다.",
    "ar": "مرحبا، هذا اختبار للغة العربية.",
    "hi": "नमस्ते, यह हिंदी भाषा का परीक्षण है।",
    "pt": "Olá, este é um teste de síntese de voz em português.",
}


def synthesize(
    url: str,
    text: str,
    output_path: Path,
    auth: str | None = None,
    model: str | None = None,
    timeout: int = 300,
) -> None:
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {auth}"

    payload: dict = {"input": text}
    if model:
        payload["model"] = model

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(resp.content)
    print(f"  -> {output_path} ({len(resp.content)} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Higgs Audio v3 TTS smoke test")
    parser.add_argument(
        "--url",
        default=os.environ.get("TTS_URL", "http://localhost:8000/v1/audio/speech"),
        help="Speech API URL (local server or Boson cloud)",
    )
    parser.add_argument(
        "--auth",
        default=os.environ.get("BOSON_API_KEY"),
        help="Bearer token (required for Boson cloud API)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("TTS_MODEL"),
        help="Model id (e.g. higgs-audio-v3-tts for Boson cloud)",
    )
    parser.add_argument(
        "--text",
        default=None,
        help="Custom text to synthesize",
    )
    parser.add_argument(
        "--lang",
        default="en",
        choices=list(SAMPLES.keys()),
        help="Preset language sample when --text is not set",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Single English sample only",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: scripts/v3/output/...)",
    )
    args = parser.parse_args()

    if args.quick:
        text = SAMPLES["en"]
        out = args.output or OUTPUT_DIR / "quick_en.wav"
        print(f"Synthesizing: {text[:60]}...")
        synthesize(args.url, text, out, args.auth, args.model)
        return

    if args.text:
        out = args.output or OUTPUT_DIR / "custom.wav"
        synthesize(args.url, args.text, out, args.auth, args.model)
        return

    text = SAMPLES[args.lang]
    out = args.output or OUTPUT_DIR / f"sample_{args.lang}.wav"
    synthesize(args.url, text, out, args.auth, args.model)


if __name__ == "__main__":
    main()
