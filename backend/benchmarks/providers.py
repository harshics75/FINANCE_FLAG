"""Provider abstraction over app.agents.llm.get_llm() — reuses the EXACT production
wiring (same base URLs, same API keys from settings) so benchmark results reflect real
inference on this app, not a reimplementation. Adding a new provider later (if the app
adds one to agents/llm.py) means adding one PROVIDERS entry here — no other changes.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from app.agents.llm import get_llm


@dataclass
class ProviderLimits:
    rpm: int              # requests per minute — client-side pacing
    daily_cap: int | None  # None = no known daily cap (e.g. Groq); int = hard stop (e.g. Nemotron free tier)
    is_free: bool
    paid_input_per_m: float | None = None   # USD per 1M input tokens, if this provider has published paid pricing
    paid_output_per_m: float | None = None  # USD per 1M output tokens


# Nemotron free tier: ~40 RPM, 200 requests/day (verified against NVIDIA's docs this
# session). Paced conservatively below the ceiling, not right up against it.
# Groq free tier limits aren't hard-verified here, so paced conservatively by default —
# adjust PROVIDERS["groq"].rpm if you know your account's actual limit.
PROVIDERS: dict[str, ProviderLimits] = {
    "groq": ProviderLimits(rpm=20, daily_cap=None, is_free=True),
    "nvidia": ProviderLimits(rpm=25, daily_cap=190, is_free=True,
                             paid_input_per_m=0.50, paid_output_per_m=2.20),
}


@dataclass
class ProviderResult:
    text: str | None
    latency_ms: float
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    retry_count: int
    error: str | None


class RateLimiter:
    """Minimum-interval pacing per provider (thread-safe) plus a hard daily-cap stop."""

    def __init__(self, limits: ProviderLimits):
        self.limits = limits
        self._min_interval = 60.0 / limits.rpm
        self._lock = threading.Lock()
        self._last_call = 0.0
        self._count = 0

    def acquire(self) -> None:
        with self._lock:
            if self.limits.daily_cap is not None and self._count >= self.limits.daily_cap:
                raise RuntimeError(
                    f"Daily cap ({self.limits.daily_cap}) reached for this provider in this run — "
                    "stopping rather than burning past the free-tier quota. Re-run tomorrow or with "
                    "--resume once the quota resets."
                )
            wait = self._min_interval - (time.monotonic() - self._last_call)
            if wait > 0:
                time.sleep(wait)
            self._last_call = time.monotonic()
            self._count += 1


_limiters: dict[str, RateLimiter] = {name: RateLimiter(limits) for name, limits in PROVIDERS.items()}


def _extract_tokens(resp) -> tuple[int | None, int | None, int | None]:
    usage = getattr(resp, "usage_metadata", None)
    if usage:
        return usage.get("input_tokens"), usage.get("output_tokens"), usage.get("total_tokens")
    meta = getattr(resp, "response_metadata", {}) or {}
    tu = meta.get("token_usage") or {}
    if tu:
        return tu.get("prompt_tokens"), tu.get("completion_tokens"), tu.get("total_tokens")
    return None, None, None


def call_provider(provider: str, prompt: str, max_retries: int = 3) -> ProviderResult:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}; add it to PROVIDERS first")
    limiter = _limiters[provider]

    retry_count = 0
    last_error: str | None = None
    while retry_count <= max_retries:
        limiter.acquire()
        start = time.monotonic()
        try:
            llm = get_llm(temperature=0.1, provider=provider)
            resp = llm.invoke([("system", "You are a precise, JSON-only financial analysis assistant."),
                               ("user", prompt)])
            latency_ms = (time.monotonic() - start) * 1000
            in_tok, out_tok, tot_tok = _extract_tokens(resp)
            return ProviderResult(
                text=resp.content, latency_ms=latency_ms,
                input_tokens=in_tok, output_tokens=out_tok, total_tokens=tot_tok,
                retry_count=retry_count, error=None,
            )
        except Exception as exc:  # noqa: BLE001 — deliberately broad: any provider failure is a data point
            last_error = f"{type(exc).__name__}: {exc}"
            retry_count += 1
            if retry_count > max_retries:
                break
            time.sleep(min(2 ** retry_count, 20))  # exponential backoff, capped

    return ProviderResult(text=None, latency_ms=0.0, input_tokens=None, output_tokens=None,
                          total_tokens=None, retry_count=retry_count - 1, error=last_error)


def estimate_cost_usd(provider: str, input_tokens: int | None, output_tokens: int | None) -> float | None:
    """Actual cost incurred is $0 on a free-tier key — this returns what it WOULD cost
    at the provider's published paid-tier rate, purely as a reference figure. Returns
    None when the provider has no published paid pricing to reference."""
    limits = PROVIDERS.get(provider)
    if not limits or limits.paid_input_per_m is None or input_tokens is None or output_tokens is None:
        return None
    return (input_tokens / 1_000_000) * limits.paid_input_per_m + \
           (output_tokens / 1_000_000) * limits.paid_output_per_m
