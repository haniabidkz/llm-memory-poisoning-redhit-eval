# RedHit (third party, not vendored)

This project builds on **RedHit**, the LLM red-teaming framework by the
Cyber Science Lab (Dr. Abbas Yazdinejad and co-authors):

- Code: https://github.com/CyberScienceLab/Our-Papers/tree/main/RedHit
- Paper: *Adaptive Red-Teaming of Large Language Models via Search, Reasoning,
  and Preference Optimization*, LLMSEC workshop @ ACL 2025,
  https://aclanthology.org/2025.llmsec-1.2/

All credit for RedHit belongs to its authors. Please cite their paper if you use it.

## Why it is fetched instead of copied

The licensing of the RedHit folder is mixed:

- the top-level `Our-Papers` repo ships a GPL-3.0 `LICENSE` and its README says
  "all codes in this repo are GNU v.3 license";
- the `RedHit/` folder itself contains an Apache-2.0 `LICENSE` (it is built on a
  fork of NVIDIA's garak, which is Apache-2.0).

Since it is not clear which terms apply to the RedHit-specific files, no RedHit
code is committed here. `fetch_redhit.sh` clones the upstream folder at a pinned
commit into `third_party/redhit/src/` (gitignored), and the scripts in this repo
import from that local copy at runtime.

```bash
bash third_party/redhit/fetch_redhit.sh
```

Pinned commit: `3093c9b1f9a1b4ce1588f4fd99460a1cecf10db3` (override with `REDHIT_COMMIT`).

garak itself (https://github.com/NVIDIA/garak, Apache-2.0) is installed from PyPI.
