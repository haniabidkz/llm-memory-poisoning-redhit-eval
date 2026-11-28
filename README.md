# LLM Memory Poisoning vs. Single-Turn Detectors

> 🚧 Work in progress

Can single-turn prompt-injection detectors catch **slow-drift memory poisoning** in a multi-turn RAG support chatbot?

A harmless-looking "rule" is planted in turn 1, nothing happens in turn 2, and in turn 3 the bot takes a harmful action because of what it remembered. This project builds on the open-source [RedHit](https://github.com/CyberScienceLab/Our-Papers/tree/main/RedHit) red-teaming framework (generator + Garak-based evaluator) and adapts it to run on a normal laptop CPU.

## Plan
- [x] Run RedHit's evaluator + garak detectors on CPU with a small open model (configurable backend)
- [ ] Build a small 3-turn RAG customer-support chatbot with persistent memory
- [ ] Write 20–30 attack trajectories (single-turn baseline vs. 3-turn slow drift) plus benign controls
- [ ] Measure attack success rate and per-turn detector catch rate
- [ ] Short technical note with results and limitations

## Setup

Tested on a CPU-only Linux box (Python 3.13, no GPU, no Docker).

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# fetch RedHit at a pinned commit (not copied into this repo, see third_party/redhit/NOTICE.md)
bash third_party/redhit/fetch_redhit.sh

# optional: change the model backend
cp .env.example .env
```

By default the target model is `Qwen/Qwen2.5-0.5B-Instruct`, run locally with transformers on CPU (float32, greedy decoding, ~3.3 GB peak RAM).
Any OpenAI-compatible endpoint works too: set `MODEL_BACKEND=openai`, `MODEL_NAME`, `OPENAI_BASE_URL` and `OPENAI_API_KEY` in `.env` (never commit it).

### Smoke test

```bash
python scripts/smoke_test.py --n 3
```

Sends a few garak PromptInject ("I hate humans") prompts to the model and scores the replies with garak detectors (`promptinject.AttackRogueString`, `mitigation.MitigationBypass`) and with RedHit's own `Evaluator`. Results go to `outputs/smoke_test.json`.

The full RedHit loop (MCTS search + a fine-tuned prompt generator served through vLLM and dspy) does not run on this CPU-only setup: the generator weights are not in the upstream repo (`final_checkpoint/` only has tokenizer files) and the code points at local paths of the original lab machine. So for now this project uses RedHit's `Evaluator` with the garak detectors it relies on, not the whole generator pipeline.

## Credits
RedHit: *Adaptive Red-Teaming of Large Language Models via Search, Reasoning, and Preference Optimization* (LLMSEC @ ACL 2025).
