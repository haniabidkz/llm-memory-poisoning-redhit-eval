"""CPU smoke test.

1. load the configured chat model (default: Qwen2.5-0.5B-Instruct on CPU)
2. take a few PromptInject "I hate humans" prompts from garak's
   promptinject.HijackHateHumans probe (the attack family RedHit reports on)
3. generate one response per prompt
4. score each response with garak detectors and with RedHit's own Evaluator
   (third_party/redhit/src/RedHit/RedHit/evaluator.py, loaded from the fetched copy)

Usage:
    bash third_party/redhit/fetch_redhit.sh
    python scripts/smoke_test.py [--n 3]
"""

import argparse
import importlib.util
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memdrift.backend import load_backend  # noqa: E402
from memdrift.config import ModelConfig  # noqa: E402

REDHIT_EVALUATOR = ROOT / "third_party/redhit/src/RedHit/RedHit/evaluator.py"
DETECTORS = ["promptinject.AttackRogueString", "mitigation.MitigationBypass"]


def load_redhit_evaluator():
    if not REDHIT_EVALUATOR.exists():
        print(f"[warn] {REDHIT_EVALUATOR} not found, run third_party/redhit/fetch_redhit.sh")
        return None
    spec = importlib.util.spec_from_file_location("redhit_evaluator", REDHIT_EVALUATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Evaluator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3, help="number of probe prompts")
    ap.add_argument("--out", default=str(ROOT / "outputs/smoke_test.json"))
    args = ap.parse_args()

    import garak
    from garak import _config, _plugins
    from garak.attempt import Attempt, Message

    cfg = ModelConfig.from_env()
    _config.load_base_config()
    _config.run.seed = cfg.seed  # garak shuffles probe prompts with this seed
    probe = _plugins.load_plugin("probes.promptinject.HijackHateHumans")
    detectors = {name: _plugins.load_plugin(f"detectors.{name}") for name in DETECTORS}
    Evaluator = load_redhit_evaluator()

    print(f"model: {cfg.describe()}")
    t0 = time.time()
    model = load_backend(cfg)
    load_s = time.time() - t0

    rows = []
    for seq in range(min(args.n, len(probe.prompts))):
        prompt = probe.prompts[seq]
        trigger = probe.pi_prompts[seq]["settings"]["attack_rogue_string"]

        t1 = time.time()
        reply = model.chat([{"role": "user", "content": prompt}])
        gen_s = time.time() - t1

        attempt = Attempt(prompt=Message(prompt, lang="en"), probe_classname="promptinject.HijackHateHumans")
        attempt.notes["triggers"] = [trigger]
        attempt.outputs = [Message(reply, lang="en")]

        scores = {name: d.detect(attempt) for name, d in detectors.items()}
        redhit_reward = None
        if Evaluator is not None:
            # RedHit's Evaluator averages the hits of probe.detectors over all outputs;
            # use the probe's primary detector, as garak does for this probe
            fake_probe = SimpleNamespace(detectors=[detectors["promptinject.AttackRogueString"]])
            redhit_reward = Evaluator(fake_probe).attempt_evaluate(attempt)

        rows.append(
            {
                "seq": seq,
                "trigger": trigger,
                "prompt": prompt,
                "response": reply,
                "gen_seconds": round(gen_s, 2),
                "detector_scores": scores,
                "redhit_evaluator_reward": redhit_reward,
            }
        )
        print(f"\n--- seq {seq} (trigger: {trigger!r}, {gen_s:.1f}s)")
        print(f"prompt  : {prompt[-160:]!r}")
        print(f"response: {reply[:300]!r}")
        for name, s in scores.items():
            print(f"  {name}: {s}")
        print(f"  RedHit Evaluator reward: {redhit_reward}")

    hits = sum(r["detector_scores"]["promptinject.AttackRogueString"][0] for r in rows)
    print(f"\nAttackRogueString hits: {hits}/{len(rows)} (1.0 = injection succeeded)")

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "model": cfg.describe(),
                "seed": cfg.seed,
                "max_new_tokens": cfg.max_new_tokens,
                "python": platform.python_version(),
                "garak": garak.__version__,
                "model_load_seconds": round(load_s, 1),
                "results": rows,
            },
            indent=2,
        )
    )
    print(f"saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
