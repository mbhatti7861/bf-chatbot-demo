"""Lightweight input/output guardrails.

A regulated environment needs content controls. This is a small, transparent,
in-app version so the behavior is visible in the demo:

  Input screening  — blocks obvious prompt-injection / jailbreak attempts and any
                     input carrying secret-like material (keys, SSNs, private keys).
  Output filtering — redacts secret/PII patterns from the model's reply (defense in
                     depth, in case a tool result or the model echoes one).

In production this is **Amazon Bedrock Guardrails** (managed PII redaction, denied
topics, and grounding checks) — the call sites here are where that would plug in.
"""
import re

# Prompt-injection / jailbreak attempts on the way in.
_INJECTION = re.compile(
    r"\b(?:ignore|disregard|forget|override)\b.{0,40}\b(?:previous|prior|above|earlier|all|your)\b"
    r".{0,30}\b(?:instruction|instructions|prompt|rules|context|guardrail|guardrails)\b"
    r"|\b(?:reveal|show|print|repeat|leak)\b.{0,30}\b(?:system\s+prompt|your\s+prompt|instructions)\b"
    r"|\byou\s+are\s+now\b|\bdeveloper\s+mode\b|\bjailbreak\b|\bDAN\b",
    re.I,
)

# Secret / PII signatures. Redacted from output; blocked on input.
_SECRETS = [
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("US SSN",         re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("private key",    re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("bearer token",   re.compile(r"\b(?:secret|token|password)\s*[:=]\s*\S{8,}", re.I)),
]


def check_input(text: str) -> dict:
    """Screen a user message. Returns {allowed, reason, flags}."""
    flags = []
    if _INJECTION.search(text):
        flags.append("prompt-injection")
    for name, pat in _SECRETS:
        if pat.search(text):
            flags.append(f"secret:{name}")

    allowed = not flags
    reason = None
    if "prompt-injection" in flags:
        reason = "Input was blocked: it looks like a prompt-injection / jailbreak attempt."
    elif flags:
        reason = "Input was blocked: it appears to contain a secret or PII (do not paste credentials)."
    return {"allowed": allowed, "reason": reason, "flags": flags}


def filter_output(text: str) -> dict:
    """Redact secret/PII patterns from a reply. Returns {text, redactions}."""
    redactions = []
    out = text
    for name, pat in _SECRETS:
        if pat.search(out):
            redactions.append(name)
            out = pat.sub("[REDACTED]", out)
    return {"text": out, "redactions": redactions}
