#!/usr/bin/env python3
"""
ollama_manager.py — Centralized Ollama interface with resilience and auto-restart.

Provides OllamaManager singleton:
  - Health checks with configurable timeout
  - LLM calls with consecutive failure tracking
  - Auto-restart via docker or systemctl on persistent failure
  - Used by audit_book.py, watchdog.py, nightly_maintenance.py
"""
from __future__ import annotations

import json
import logging
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

logger = logging.getLogger(__name__)


class OllamaManager:
    HEALTH_TIMEOUT           = 10   # seconds for health check
    TASK_TIMEOUT             = 30   # seconds per LLM task
    MAX_CONSECUTIVE_FAILURES = 3
    RESTART_WAIT             = 60   # seconds to wait after restart
    MAX_RESTART_ATTEMPTS     = 3

    def __init__(self) -> None:
        self.consecutive_failures = 0
        self._restart_attempts    = 0

    # ── Health ────────────────────────────────────────────────────────────────

    def is_healthy(self) -> bool:
        """Quick health check — responds within HEALTH_TIMEOUT?"""
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
            with urllib.request.urlopen(req, timeout=self.HEALTH_TIMEOUT) as resp:
                return resp.status == 200
        except Exception:
            return False

    def wait_until_healthy(self, max_wait: int = 120) -> bool:
        """Poll health check every 5 seconds until max_wait seconds."""
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            if self.is_healthy():
                return True
            time.sleep(5)
        return False

    # ── Restart ───────────────────────────────────────────────────────────────

    def restart_ollama(self) -> bool:
        """
        Restart Ollama. Tries docker first, then systemctl.
        Waits RESTART_WAIT seconds then health-checks.
        Returns True if healthy after restart.
        Logs every step.
        """
        logger.info("OllamaManager: restart attempt #%d — trying docker", self._restart_attempts + 1)

        # Try docker restart
        try:
            r = subprocess.run(
                ["docker", "restart", "ollama"],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0:
                logger.info("OllamaManager: docker restart OK — waiting %ds for startup", self.RESTART_WAIT)
                time.sleep(self.RESTART_WAIT)
                if self.wait_until_healthy(max_wait=60):
                    logger.info("OllamaManager: Ollama healthy after docker restart")
                    return True
                logger.warning("OllamaManager: not healthy after docker restart (waited %ds+60s)", self.RESTART_WAIT)
        except Exception as e:
            logger.warning("OllamaManager: docker restart failed: %s", e)

        # Fallback: systemctl
        logger.info("OllamaManager: trying systemctl restart ollama")
        try:
            r2 = subprocess.run(
                ["systemctl", "restart", "ollama"],
                capture_output=True, text=True, timeout=30,
            )
            if r2.returncode == 0:
                logger.info("OllamaManager: systemctl restart OK — waiting %ds", self.RESTART_WAIT)
                time.sleep(self.RESTART_WAIT)
                if self.wait_until_healthy(max_wait=60):
                    logger.info("OllamaManager: Ollama healthy after systemctl restart")
                    return True
                logger.warning("OllamaManager: not healthy after systemctl restart")
        except Exception as e:
            logger.warning("OllamaManager: systemctl restart failed: %s", e)

        logger.error("OllamaManager: all restart strategies failed")
        return False

    # ── LLM call ─────────────────────────────────────────────────────────────

    def call(self, prompt: str, timeout: int | None = None) -> dict | None:
        """
        Call Ollama with full error handling.

        - Consecutive failure counter increments on timeout/error.
        - On reaching MAX_CONSECUTIVE_FAILURES: attempts restart before returning None.
        - After successful restart: resets counters and retries once.
        - Returns parsed JSON dict or None if unavailable.
        """
        if timeout is None:
            timeout = self.TASK_TIMEOUT

        # Threshold reached — attempt restart before proceeding
        if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            if self._restart_attempts >= self.MAX_RESTART_ATTEMPTS:
                return None  # gave up
            logger.warning(
                "OllamaManager: %d consecutive failures — attempting restart #%d",
                self.consecutive_failures, self._restart_attempts + 1,
            )
            self._restart_attempts += 1
            if self.restart_ollama():
                self.consecutive_failures = 0
                # fall through to make one attempt
            else:
                return None

        body = json.dumps({
            "model":  OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
                raw  = data.get("response", "").strip()
                raw  = raw.lstrip("```json").lstrip("```").rstrip("```").strip()
                result = json.loads(raw)
                # Success — reset counters
                self.consecutive_failures = 0
                self._restart_attempts    = 0
                return result
        except json.JSONDecodeError as e:
            logger.warning("OllamaManager: JSON parse error: %s", e)
            self.consecutive_failures += 1
            return None
        except Exception as e:
            logger.warning("OllamaManager: request failed: %s", e)
            self.consecutive_failures += 1
            return None

    def reset(self) -> None:
        """Reset failure counters (e.g. after a book is completed successfully)."""
        self.consecutive_failures = 0
        self._restart_attempts    = 0


# Module-level singleton — import this from other scripts
ollama = OllamaManager()
