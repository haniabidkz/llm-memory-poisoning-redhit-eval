"""Settings read from environment variables (optionally from a local .env file)."""

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass


@dataclass
class ModelConfig:
    backend: str = "hf"
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    dtype: str = "float32"  # bf16 halves RAM but greedy output drifted between runs
    max_new_tokens: int = 128
    seed: int = 1373
    base_url: str | None = None
    api_key: str | None = None

    @classmethod
    def from_env(cls) -> "ModelConfig":
        return cls(
            backend=os.getenv("MODEL_BACKEND", cls.backend).lower(),
            model_name=os.getenv("MODEL_NAME") or cls.model_name,
            dtype=os.getenv("MODEL_DTYPE", cls.dtype),
            max_new_tokens=int(os.getenv("MAX_NEW_TOKENS", cls.max_new_tokens)),
            seed=int(os.getenv("SEED", cls.seed)),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            api_key=os.getenv("OPENAI_API_KEY") or None,
        )

    def describe(self) -> str:
        # never print the key itself
        where = self.base_url or "default endpoint"
        if self.backend == "openai":
            return f"openai-compatible:{self.model_name} @ {where}"
        return f"hf:{self.model_name} (cpu, {self.dtype})"
