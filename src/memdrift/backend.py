"""Chat model backends.

hf      - local transformers model on CPU (default: Qwen2.5-0.5B-Instruct)
openai  - any OpenAI-compatible chat completions endpoint
"""

from __future__ import annotations

import random

from .config import ModelConfig

Message = dict[str, str]  # {"role": ..., "content": ...}


class ChatBackend:
    def chat(self, messages: list[Message]) -> str:
        raise NotImplementedError


class HFBackend(ChatBackend):
    def __init__(self, cfg: ModelConfig):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.cfg = cfg
        self.torch = torch
        random.seed(cfg.seed)
        torch.manual_seed(cfg.seed)
        dtype = getattr(torch, cfg.dtype)
        self.tok = AutoTokenizer.from_pretrained(cfg.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            cfg.model_name, dtype=dtype, low_cpu_mem_usage=True
        )
        self.model.eval()

    def chat(self, messages: list[Message]) -> str:
        torch = self.torch
        inputs = self.tok.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
        )
        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.cfg.max_new_tokens,
                do_sample=False,  # greedy, so runs are repeatable
                pad_token_id=self.tok.eos_token_id,
            )
        new_tokens = out[0][inputs["input_ids"].shape[1]:]
        return self.tok.decode(new_tokens, skip_special_tokens=True).strip()


class OpenAICompatBackend(ChatBackend):
    def __init__(self, cfg: ModelConfig):
        from openai import OpenAI

        if not cfg.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set (MODEL_BACKEND=openai)")
        self.cfg = cfg
        self.client = OpenAI(base_url=cfg.base_url, api_key=cfg.api_key)

    def chat(self, messages: list[Message]) -> str:
        resp = self.client.chat.completions.create(
            model=self.cfg.model_name,
            messages=messages,
            max_tokens=self.cfg.max_new_tokens,
            temperature=0,
            seed=self.cfg.seed,
        )
        return (resp.choices[0].message.content or "").strip()


def load_backend(cfg: ModelConfig | None = None) -> ChatBackend:
    cfg = cfg or ModelConfig.from_env()
    if cfg.backend == "hf":
        return HFBackend(cfg)
    if cfg.backend == "openai":
        return OpenAICompatBackend(cfg)
    raise ValueError(f"unknown MODEL_BACKEND: {cfg.backend!r} (use 'hf' or 'openai')")
