"""
Central AI client — routes all AI calls to the correct
provider and model based on config/ai_settings.json.

Usage:
    from ai_client import AIClient
    client = AIClient()

    # Text generation
    response = client.generate("chunk_tagging",
                               prompt="Classify this chunk...")

    # Vision (image + text)
    response = client.generate_vision("book_metadata",
                                      image_path=Path("page1.png"),
                                      prompt="Extract title...")

    # Get current config for a use case
    cfg = client.get_use_case("chunk_tagging")
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

AI_SETTINGS_PATH = Path("/root/medical-rag/config/ai_settings.json")


class AIClient:
    def __init__(self):
        self._settings = self._load_settings()

    def _load_settings(self) -> dict:
        try:
            return json.loads(AI_SETTINGS_PATH.read_text())
        except Exception as e:
            log.error("Failed to load ai_settings.json: %s", e)
            return {}

    def reload(self):
        """Reload settings from disk (called after UI update)."""
        self._settings = self._load_settings()

    def get_use_case(self, use_case: str) -> dict:
        """Return current provider/model config for a use case."""
        return self._settings.get("use_cases", {}).get(use_case, {})

    def get_providers(self) -> dict:
        return self._settings.get("providers", {})

    def generate(self, use_case: str, prompt: str,
                 system: Optional[str] = None,
                 max_tokens: int = 1000) -> str:
        """
        Generate text using the configured provider for use_case.
        Returns the response text or raises an exception.
        """
        cfg      = self.get_use_case(use_case)
        provider = cfg.get("provider", "ollama")
        model    = cfg.get("model", "llama3.1:8b")

        log.info("AI generate: use_case=%s provider=%s model=%s",
                 use_case, provider, model)

        if provider == "ollama":
            return self._ollama_generate(model, prompt, system, max_tokens)
        elif provider == "anthropic":
            return self._anthropic_generate(model, prompt, system, max_tokens)
        elif provider == "gemini":
            return self._gemini_generate(model, prompt, system, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate_vision(self, use_case: str,
                        image_path: Path,
                        prompt: str,
                        max_tokens: int = 1000) -> str:
        """
        Generate text from image + prompt.
        Only works with vision-capable providers.
        """
        cfg      = self.get_use_case(use_case)
        provider = cfg.get("provider", "gemini")
        model    = cfg.get("model", "gemini-2.5-flash")

        if not cfg.get("supports_vision", False):
            raise ValueError(
                f"Use case '{use_case}' does not support vision. "
                f"Change provider to gemini or anthropic."
            )

        log.info("AI vision: use_case=%s provider=%s model=%s",
                 use_case, provider, model)

        if provider == "gemini":
            return self._gemini_vision(model, image_path, prompt, max_tokens)
        elif provider == "anthropic":
            return self._anthropic_vision(model, image_path, prompt, max_tokens)
        else:
            raise ValueError(f"Provider '{provider}' does not support vision")

    # ── Ollama ────────────────────────────────────────────────────────────────

    def _ollama_generate(self, model: str, prompt: str,
                         system: Optional[str], max_tokens: int) -> str:
        import httpx
        base_url = self.get_providers().get("ollama", {}).get(
            "base_url", "http://localhost:11434"
        )
        payload = {
            "model":   model,
            "prompt":  prompt,
            "stream":  False,
            "options": {"num_predict": max_tokens},
        }
        if system:
            payload["system"] = system
        r = httpx.post(f"{base_url}/api/generate", json=payload, timeout=120)
        r.raise_for_status()
        return r.json().get("response", "")

    # ── Anthropic ─────────────────────────────────────────────────────────────

    def _anthropic_generate(self, model: str, prompt: str,
                            system: Optional[str], max_tokens: int) -> str:
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=api_key)
        kwargs: dict = {
            "model":      model,
            "max_tokens": max_tokens,
            "messages":   [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        msg = client.messages.create(**kwargs)
        return msg.content[0].text

    def _anthropic_vision(self, model: str, image_path: Path,
                          prompt: str, max_tokens: int) -> str:
        import anthropic
        import base64
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        img_data  = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
        media_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                     ".png": "image/png",  ".webp": "image/webp"}
        media     = media_map.get(image_path.suffix.lower(), "image/png")
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {
                    "type":       "base64",
                    "media_type": media,
                    "data":       img_data,
                }},
                {"type": "text", "text": prompt},
            ]}],
        )
        return msg.content[0].text

    # ── Gemini ────────────────────────────────────────────────────────────────

    def _gemini_generate(self, model: str, prompt: str,
                         system: Optional[str], max_tokens: int) -> str:
        from google import genai
        from google.genai import types
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        client      = genai.Client(api_key=api_key)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        if response.text is not None:
            return response.text
        # Fallback: extract text from candidates when response.text is None
        # (can happen on MAX_TOKENS with some SDK versions)
        for cand in (response.candidates or []):
            for part in (cand.content.parts if cand.content else []):
                if part.text:
                    return part.text
        return ""

    def _gemini_vision(self, model: str, image_path: Path,
                       prompt: str, max_tokens: int) -> str:
        from google import genai
        from google.genai import types
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        client   = genai.Client(api_key=api_key)
        img_data = image_path.read_bytes()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png",  ".webp": "image/webp"}
        mime     = mime_map.get(image_path.suffix.lower(), "image/png")
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=img_data, mime_type=mime),
                prompt,
            ],
            config=types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        if response.text is not None:
            return response.text
        for cand in (response.candidates or []):
            for part in (cand.content.parts if cand.content else []):
                if part.text:
                    return part.text
        return ""


# ── Save settings ─────────────────────────────────────────────────────────────

def save_ai_settings(settings: dict) -> None:
    """Save updated settings to disk atomically."""
    tmp = AI_SETTINGS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False))
    tmp.replace(AI_SETTINGS_PATH)
