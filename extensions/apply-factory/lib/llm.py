"""
LLM call abstraction. Points to whatever opencode is using.
Set APPLY_LLM_BACKEND env var to switch: opencode | kimi | anthropic.
"""
import json
import os
import subprocess
from typing import Any


def call(prompt: str, *, system: str | None = None,
         temperature: float = 0.1) -> str:
    backend = os.environ.get("APPLY_LLM_BACKEND", "opencode")

    if backend == "opencode":
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        result = subprocess.run(
            ["opencode", "run", "--stdin"],
            input=full_prompt, capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"opencode failed: {result.stderr}")
        return result.stdout.strip()

    if backend == "kimi":
        import requests
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        r = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}"},
            json={"model": "kimi-k2-0711-preview", "messages": messages,
                  "temperature": temperature},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    if backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return msg.content[0].text.strip()

    raise ValueError(f"Unknown backend: {backend}")


def call_json(prompt: str, *, system: str | None = None,
              temperature: float = 0.1) -> Any:
    raw = call(prompt, system=system, temperature=temperature)
    clean = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON:\n{raw}") from e
