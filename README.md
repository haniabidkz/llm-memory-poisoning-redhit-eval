# LLM Memory Poisoning vs. Single-Turn Detectors

> 🚧 Work in progress

Can single-turn prompt-injection detectors catch **slow-drift memory poisoning** in a multi-turn RAG support chatbot?

A harmless-looking "rule" is planted in turn 1, nothing happens in turn 2, and in turn 3 the bot takes a harmful action because of what it remembered. This project builds on the open-source [RedHit](https://github.com/CyberScienceLab/Our-Papers/tree/main/RedHit) red-teaming framework (generator + Garak-based evaluator) and adapts it to run on a normal laptop CPU.

## Plan
- [ ] Run RedHit on CPU with a small open model (configurable backend)
- [ ] Build a small 3-turn RAG customer-support chatbot with persistent memory
- [ ] Write 20–30 attack trajectories (single-turn baseline vs. 3-turn slow drift) plus benign controls
- [ ] Measure attack success rate and per-turn detector catch rate
- [ ] Short technical note with results and limitations

## Credits
RedHit: *Adaptive Red-Teaming of Large Language Models via Search, Reasoning, and Preference Optimization* (LLMSEC @ ACL 2025).
