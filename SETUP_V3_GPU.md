# Higgs Audio v3 — GPU PC setup

Higgs Audio **v3** (100+ languages, voice cloning, emotion/style control) does **not** use the `boson_multimodal` code in this repo. On-device inference is served with **[SGLang-Omni](https://github.com/sgl-project/sglang-omni)** and weights from Hugging Face.

This repo holds **setup scripts and smoke tests** so you can clone once on your GPU machine and run a repeatable install.

## What you need

| Requirement | Notes |
|-------------|--------|
| **OS** | Linux or WSL2 on Windows (NVIDIA drivers + CUDA in WSL) |
| **GPU** | NVIDIA with **≥16 GB VRAM** (24 GB+ recommended for comfortable batching) |
| **Disk** | ~12 GB for model weights + ~5 GB for SGLang-Omni / deps |
| **Accounts** | [Hugging Face](https://huggingface.co/settings/tokens) token (model access) |

Optional: [Boson AI API key](https://boson.ai/workspace) for cloud smoke tests without a GPU.

## Quick start (GPU PC)

```bash
git clone https://github.com/boson-ai/higgs-audio.git
cd higgs-audio

# Hugging Face login (if not already logged in)
hf auth login

# One-shot install: SGLang-Omni + model weights
./scripts/v3/setup_gpu.sh

# Start the local OpenAI-compatible server
./scripts/v3/serve.sh
```

In another terminal:

```bash
cd higgs-audio
source scripts/v3/.env 2>/dev/null || true
python scripts/v3/test_client.py --quick
python scripts/v3/test_multilingual.py --languages en,zh,ja,es,fr,de
```

Outputs are written to `scripts/v3/output/`.

## Docker path (recommended by SGLang-Omni)

If bare-metal install fails (flash-attn, UCX, etc.), use the official image:

```bash
docker pull lmsysorg/sglang-omni:dev
docker run -it --shm-size 32g --gpus all --ipc host --network host --privileged \
  lmsysorg/sglang-omni:dev /bin/zsh

# inside container:
git clone https://github.com/sgl-project/sglang-omni.git && cd sglang-omni
uv venv .venv -p 3.12 && source .venv/bin/activate
uv pip install -v -e .

hf download bosonai/higgs-audio-v3-tts-4b
sgl-omni serve --model-path bosonai/higgs-audio-v3-tts-4b --port 8000
```

## API reference

Server exposes `POST http://localhost:8000/v1/audio/speech` (WAV by default).

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, how are you?"}' \
  --output hello.wav
```

Inline control tokens (emotion, style, prosody, sfx) go in `input`. Full cookbook:
- [SGLang-Omni Higgs TTS](https://sgl-project.github.io/sglang-omni/cookbook/higgs_tts.html)
- [Model card](https://huggingface.co/bosonai/higgs-audio-v3-tts-4b)

## Cloud smoke test (no GPU)

```bash
export BOSON_API_KEY=bai-xxxx
python scripts/v3/test_client.py --url https://api.boson.ai/v1/audio/speech \
  --auth "$BOSON_API_KEY" --model higgs-audio-v3-tts
```

## v2 vs v3

| | v3 (this guide) | v2 / v2.5 (this repo code) |
|--|-----------------|----------------------------|
| Languages | 100+ | fewer |
| Serve stack | SGLang-Omni | `boson_multimodal` + `examples/generation.py` |
| Model | `bosonai/higgs-audio-v3-tts-4b` | `bosonai/higgs-audio-v2-generation-3B-base` |
| Setup | `scripts/v3/setup_gpu.sh` | `pip install -r requirements.txt && pip install -e .` |

See [README_V2.md](./README_V2.md) for v2.

## License

v3 weights are under the **Boson Higgs Audio v3 Research and Non-Commercial License**. Commercial / production use requires a separate license from Boson AI.
