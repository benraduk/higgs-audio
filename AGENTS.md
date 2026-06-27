# Agent guide — Higgs Audio v3 on GPU PC

This document is for **Cursor / coding agents** setting up **on-device Higgs Audio v3 TTS** on the user's **NVIDIA GPU PC** (Linux or WSL2). Read this before running commands or editing files.

Human-readable companion: [SETUP_V3_GPU.md](./SETUP_V3_GPU.md).

---

## Critical context (read first)

1. **Target model:** Higgs Audio **v3** — `bosonai/higgs-audio-v3-tts-4b` (100+ languages, voice cloning, inline emotion/style/prosody/sfx control).
2. **v3 does NOT use the Python package in this repo.** The `boson_multimodal` package and `pip install -e .` path are for **v2 / v2.5 only** ([README_V2.md](./README_V2.md)).
3. **v3 on-device inference** is served by **[SGLang-Omni](https://github.com/sgl-project/sglang-omni)** (`sgl-omni serve`), not by `examples/generation.py` or `HiggsAudioServeEngine`.
4. **This repo's role:** orchestration scripts under `scripts/v3/`, smoke tests, and docs. The heavy runtime lives in a **sibling clone** of `sglang-omni` (default: `../sglang-omni` next to this repo).

Do not spend time fixing `boson_multimodal` imports when the user wants v3.

---

## Goal state ("fully set up")

The setup is complete when all of the following are true:

| Check | How to verify |
|-------|----------------|
| NVIDIA GPU visible | `nvidia-smi` shows GPU name and driver |
| Hugging Face auth | `hf auth whoami` succeeds |
| Model weights local | `models/bosonai/higgs-audio-v3-tts-4b/` exists (or HF cache populated) |
| SGLang-Omni installed | `../sglang-omni/.venv` exists; `sgl-omni --help` works inside that venv |
| Config written | `scripts/v3/.env` exists (created by setup script) |
| Server runs | `./scripts/v3/serve.sh` starts without error |
| Inference works | `python scripts/v3/test_client.py --quick` writes `scripts/v3/output/quick_en.wav` |

---

## Prerequisites

| Requirement | Minimum | Notes |
|-------------|---------|--------|
| OS | Linux native or **WSL2** on Windows | macOS is not a target for GPU serving |
| GPU | NVIDIA, **≥16 GB VRAM** | 24 GB+ recommended; check with `nvidia-smi` |
| Disk | ~17 GB free | ~12 GB weights + ~5 GB deps |
| Python | **3.12** for SGLang-Omni | Setup script uses `uv venv -p 3.12` |
| Network | Hugging Face access | For `hf download` |
| Account | Hugging Face token | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |

Optional: `BOSON_API_KEY` from [boson.ai/workspace](https://boson.ai/workspace) for cloud smoke tests without a local server.

---

## Repository layout (what matters for v3)

```
higgs-audio/                          # this repo (clone target)
├── AGENTS.md                         # this file
├── SETUP_V3_GPU.md                   # human setup guide
├── README.md                         # v3 overview + API / self-host summary
├── README_V2.md                      # v2 only — ignore for v3 setup
├── scripts/v3/
│   ├── setup_gpu.sh                  # one-shot install (run this first)
│   ├── serve.sh                      # start local TTS server
│   ├── env.example                   # config template
│   ├── .env                          # generated paths (after setup)
│   ├── test_client.py                # single-sample smoke test
│   ├── test_multilingual.py          # batch language smoke test
│   └── output/                       # generated WAV files
├── models/
│   └── bosonai/higgs-audio-v3-tts-4b/   # downloaded weights (after setup)
└── boson_multimodal/                 # v2 code — not used for v3

../sglang-omni/                       # sibling clone (default location)
├── .venv/                            # SGLang-Omni Python env
└── docs/_static/audio/               # reference clips for voice-clone examples
```

---

## Setup workflow (agent execution order)

Run from the repo root unless noted. Use a real shell with network access.

### Step 0 — Confirm environment

```bash
nvidia-smi
uname -a
```

If `nvidia-smi` fails on Windows, ensure WSL2 + NVIDIA drivers are installed. Do not proceed with GPU serving until this works.

### Step 1 — Clone repo (if not already present)

```bash
git clone https://github.com/boson-ai/higgs-audio.git
cd higgs-audio
```

If the user already cloned, `cd` to their path and `git pull` if they want latest scripts.

### Step 2 — Hugging Face authentication

```bash
hf auth whoami || hf auth login
```

If `hf` is missing, `setup_gpu.sh` installs it. User must complete interactive login if not authenticated.

### Step 3 — Run automated setup

```bash
chmod +x scripts/v3/setup_gpu.sh scripts/v3/serve.sh
./scripts/v3/setup_gpu.sh
```

This script:

1. Clones `https://github.com/sgl-project/sglang-omni.git` to `../sglang-omni` (unless `SGLANG_OMNI_DIR` is set)
2. Creates `sglang-omni/.venv` with Python 3.12 via `uv`
3. Installs SGLang-Omni editable (`uv pip install -e .`)
4. Downloads `bosonai/higgs-audio-v3-tts-4b` to `models/bosonai/higgs-audio-v3-tts-4b`
5. Writes `scripts/v3/.env` with paths

**Expect:** long install (flash-attn, torch, etc.) and a large download. Do not interrupt.

### Step 4 — Install test client deps

Smoke tests only need `requests` (any Python 3.10+ on the host):

```bash
pip install requests
# or: python3 -m pip install requests
```

### Step 5 — Start server (long-running)

```bash
./scripts/v3/serve.sh
```

Server listens on `http://0.0.0.0:8000` by default. Endpoint: `POST /v1/audio/speech`.

Leave this running in a terminal or background process. Model load can take several minutes on first start.

### Step 6 — Verify inference

In a **second terminal**, from repo root:

```bash
source scripts/v3/.env 2>/dev/null || true
python scripts/v3/test_client.py --quick
python scripts/v3/test_multilingual.py --languages en,zh,ja,es,fr,de,ko,ar,hi,pt
```

Confirm WAV files in `scripts/v3/output/` are non-empty and play as speech.

---

## Configuration (`scripts/v3/.env`)

Created by `setup_gpu.sh`. Key variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODEL_ID` | `bosonai/higgs-audio-v3-tts-4b` | Hugging Face model id |
| `MODEL_LOCAL_DIR` | `models/bosonai/higgs-audio-v3-tts-4b` | Local weight path |
| `SGLANG_OMNI_DIR` | `../sglang-omni` | SGLang-Omni clone |
| `SERVE_PORT` | `8000` | Server port |
| `SERVE_HOST` | `0.0.0.0` | Bind address |

Copy `scripts/v3/env.example` to `scripts/v3/.env` and edit if paths differ on the user's machine.

---

## API usage (local server)

### Zero-shot TTS

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, how are you?"}' \
  --output hello.wav
```

### Voice cloning

Reference audio paths must be allowed by `--allowed-local-media-path` (set in `serve.sh` to SGLang-Omni's `docs/_static/audio`). Supplying reference **text** improves quality.

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Have a nice day.",
    "references": [{
      "audio_path": "docs/_static/audio/male-voice.wav",
      "text": "Hey, Adam here. Let'\''s create something that feels real, sounds human, and connects every time."
    }],
    "temperature": 0.8,
    "top_k": 50,
    "max_new_tokens": 1024
  }' \
  --output cloned.wav
```

Run curl from `SGLANG_OMNI_DIR` or use absolute paths for `audio_path`.

### Inline control tokens

Embed tags in `input`. Lead with delivery tokens (`<|emotion:…|>`, `<|style:…|>`, speed/pitch/expressive prosody). Pair `<|sfx:…|>` with onomatopoeia immediately after (e.g. `<|sfx:laughter|>Hehe`).

Full reference: [SGLang-Omni Higgs TTS cookbook](https://sgl-project.github.io/sglang-omni/cookbook/higgs_tts.html).

---

## Cloud fallback (no local server)

If GPU setup is blocked, verify v3 API access:

```bash
export BOSON_API_KEY=bai-xxxx
python scripts/v3/test_client.py \
  --url https://api.boson.ai/v1/audio/speech \
  --auth "$BOSON_API_KEY" \
  --model higgs-audio-v3-tts \
  --quick
```

This does **not** replace on-device setup; it only confirms API credentials and model behavior.

---

## Docker fallback (when bare-metal install fails)

SGLang-Omni recommends Docker when **flash-attn**, **UCX**, or CUDA toolchain issues block `uv pip install -e .`.

```bash
docker pull lmsysorg/sglang-omni:dev
docker run -it --shm-size 32g --gpus all --ipc host --network host --privileged \
  lmsysorg/sglang-omni:dev /bin/zsh
```

Inside container:

```bash
git clone https://github.com/sgl-project/sglang-omni.git && cd sglang-omni
uv venv .venv -p 3.12 && source .venv/bin/activate
uv pip install -v -e .
hf download bosonai/higgs-audio-v3-tts-4b
sgl-omni serve --model-path bosonai/higgs-audio-v3-tts-4b --port 8000
```

Mount the user's `higgs-audio` repo if they need `scripts/v3/test_client.py` from inside Docker:

```bash
docker run -it --shm-size 32g --gpus all --ipc host --network host --privileged \
  -v /path/to/higgs-audio:/workspace/higgs-audio \
  lmsysorg/sglang-omni:dev /bin/zsh
```

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `nvidia-smi` fails | Drivers / WSL GPU not configured | Fix NVIDIA stack before SGLang install |
| `uv pip install` fails on flash-attn | CUDA / compiler mismatch | Use Docker path above |
| `hf download` 401/403 | Not logged in or no model access | `hf auth login`; accept license on model page |
| `serve.sh`: venv not found | Setup incomplete | Re-run `./scripts/v3/setup_gpu.sh` |
| CUDA OOM on serve | GPU < 16 GB or other processes using VRAM | Free VRAM; close other GPU apps; consider smaller batch / single request |
| Server up but test times out | Model still loading | Wait 2–5 min; retry `test_client.py --quick` |
| Voice clone: file not found | Path outside allowed media dir | Use paths under `sglang-omni/docs/_static/audio` or adjust `--allowed-local-media-path` |
| User asks for v2 examples | Wrong stack | Point to `README_V2.md`, `pip install -r requirements.txt && pip install -e .` |

---

## What agents should NOT do

- Do **not** run `pip install -e .` and `examples/generation.py` for v3 — that is the v2 stack.
- Do **not** assume `bosonai/higgs-tts-3-4b` and `bosonai/higgs-audio-v3-tts-4b` are different products without checking; **use `bosonai/higgs-audio-v3-tts-4b`** (matches README and SGLang-Omni docs).
- Do **not** commit `scripts/v3/.env`, API keys, or downloaded `models/` weights to git.
- Do **not** force-push or amend git history unless the user explicitly requests it.

---

## v2 vs v3 (quick reference)

| | v3 (default for this PC) | v2 / v2.5 |
|--|--------------------------|-----------|
| Languages | 100+ | fewer |
| Serve | SGLang-Omni `sgl-omni serve` | `boson_multimodal.serve.serve_engine` |
| Model | `bosonai/higgs-audio-v3-tts-4b` | `bosonai/higgs-audio-v2-generation-3B-base` |
| Setup | `scripts/v3/setup_gpu.sh` | `pip install -r requirements.txt && pip install -e .` |
| Docs | [SETUP_V3_GPU.md](./SETUP_V3_GPU.md), [cookbook](https://sgl-project.github.io/sglang-omni/cookbook/higgs_tts.html) | [README_V2.md](./README_V2.md) |

---

## License note

Higgs Audio v3 weights: **Boson Higgs Audio v3 Research and Non-Commercial License**. Commercial / production / revenue use requires a separate license from Boson AI. Do not advise deploying to production without checking license terms.

---

## External references

- Model card: https://huggingface.co/bosonai/higgs-audio-v3-tts-4b
- SGLang-Omni install: https://github.com/sgl-project/sglang-omni/blob/main/docs/get_started/installation.md
- Higgs TTS cookbook: https://sgl-project.github.io/sglang-omni/cookbook/higgs_tts.html
- Boson cloud API: https://docs.boson.ai/models/higgs-audio-tts/overview
