---
name: local-llm-advisor
description: Recommend which local LLM model(s) to run on a given Mac, sized to its unified memory. Does live web research because the model landscape changes monthly (Gemma QAT, Qwen, Llama, Apple Foundation Models). Triggers on "which local model", "what model should I run", "pick a local LLM", "local model for my Mac", or sizing a model to RAM.
---

# Local LLM Advisor

Recommend local models for the user's Apple Silicon Macs. The model landscape moves fast: **never answer from memory alone.** Run fresh web research every time, then size candidates to the hardware's unified memory.

If the user does not name the hardware, ask for the machine and its unified memory before recommending. A local section appended to this skill may list default machines.

## Process

### 1. Pin the inputs
Confirm or assume:
- **Machine + unified RAM** (drives everything)
- **Use case**: pick the dominant one: general chat, coding assist, agentic/tool-use, long-context, vision/multimodal, fast-and-light
- **Runtime**: Ollama (headless/scriptable), LM Studio (GUI + MLX), or Jan (open-source). Affects quant format (GGUF vs MLX).

### 2. Compute the memory budget (do the math, show it)
Apple Silicon shares one memory pool. Rules of thumb:
- macOS + apps eat ~8-10GB. On a 32GB machine, keep **model + KV cache under ~18-20GB** to stay responsive. (The GPU can be allowed more via `sudo sysctl iogpu.wired_limit_mb=N`, but don't assume the user has done that.)
- **Weights ≈ params × bytes-per-param.** Q4 ≈ ~0.55 GB per billion params; Q5 ≈ ~0.7; Q6 ≈ ~0.8; Q8 ≈ ~1.1; fp16 ≈ 2.0.
  - 8B Q4 ≈ ~5GB · 14B Q4 ≈ ~8-9GB · 27-32B dense Q4 ≈ ~18-20GB (tight on 32GB) · 70B needs ~40GB+ (Studio only).
- **MoE models** (e.g. Qwen3-30B-A3B) cost RAM for *total* params but compute only *active* params: big quality-per-speed win when they fit.
- **KV cache** grows with context length × layers; long-context use can add several GB. Leave headroom.

State the realistic VRAM ceiling for this machine before ranking.

### 3. Research the current field (REQUIRED: use WebSearch / WebFetch)
Search for the present state, e.g.:
- "best local LLM [month year]", "Gemma 3 QAT quantized benchmarks", "Qwen3 vs Llama local", "[use case] local model leaderboard"
- Check whatever is current: **Gemma 3 + QAT quants**, **Qwen3** family, **Llama 3.3/4**, **Mistral/Devstral**, **DeepSeek** distills, coding-specific (Qwen2.5-Coder, Devstral), vision (Gemma 3, Qwen-VL).
- Note **license** (some are non-commercial or gated) and **release recency**: prefer models < ~6 months old unless an older one still leads its size class.
- Verify availability in the chosen runtime (Ollama library tag, LM Studio / MLX-community repo).

Do not trust the anchors above as final: they are starting points to confirm or replace with what you find.

### 4. Watch the moving targets
Flag these when relevant, because they reshape the answer:
- **Gemma QAT**: quantization-aware-trained quants that hold quality far better than naive Q4. Often the best size/quality pick right now.
- **Apple Foundation Models (AFM)**: on-device models exposed via the Foundation Models framework / new Siri. As these mature they become a zero-install, OS-native option for some tasks. Check current state and note if it now covers the use case.
- **MLX vs GGUF**: MLX builds are usually faster on Apple Silicon; GGUF is more portable (Ollama). Match to the chosen runtime.

### 5. Rank and recommend

## Output format

1. **Budget line**: one sentence: this machine's realistic model ceiling and why.
2. **Ranked table**: 3-5 candidates:

   | Rank | Model (quant) | ~RAM | Why it fits this use case | Pull command |
   |---|---|---|---|---|

   Pull command = real, runnable (`ollama pull ...` or LM Studio / MLX repo id).
3. **Top pick**: one model, one sentence on why over the runner-up.
4. **What to download before going offline**: if airplane/offline context, list 2-3 to pull on wifi first.
5. **Watch list**: what's about to change (next Gemma/Qwen/Llama drop, AFM status) that would revise this in a few months.

## What NOT to do

- Don't recommend from memory, if WebSearch is unavailable, say so and clearly mark the answer as possibly stale.
- Don't suggest models that won't fit the memory budget (the most common mistake). Show the math.
- Don't ignore license constraints: flag gated or non-commercial models.
- Don't bury the pick. One clear top recommendation, then alternatives.
