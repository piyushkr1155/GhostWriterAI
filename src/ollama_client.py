"""Client for communicating with the local Ollama HTTP API."""
import time
import json
import logging
from typing import Dict, Any, List, Optional, Generator
import requests

from src.config import config

logger = logging.getLogger(__name__)

class OllamaClientError(Exception):
    """Base exception for Ollama client errors."""
    pass

class OllamaConnectionError(OllamaClientError):
    """Raised when Ollama local HTTP service cannot be reached."""
    pass

class ModelNotFoundError(OllamaClientError):
    """Raised when the specified model is not downloaded in Ollama."""
    pass

class OllamaTimeoutError(OllamaClientError):
    """Raised when an inference request times out."""
    pass


class OllamaClient:
    """Interacts with local Ollama service without cloud transmission."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        self.base_url = (base_url or config.ollama_base_url).rstrip("/")
        self.default_model = default_model or config.default_model
        self.timeout = timeout or config.timeout_seconds

    def _normalize_model_name(self, name: str) -> str:
        """Normalize model name for comparison (e.g. 'llama3.2' -> 'llama3.2:latest')."""
        name = name.strip()
        if ":" not in name:
            return f"{name}:latest"
        return name

    def check_health(self, target_model: Optional[str] = None) -> Dict[str, Any]:
        """Check Ollama connectivity, ping latency, and model availability.

        Returns:
            Dict containing:
                - is_running: bool
                - latency_ms: float
                - models: List[str]
                - active_model: str
                - is_model_available: bool
                - message: str
        """
        model_to_check = target_model or self.default_model
        start_time = time.perf_counter()

        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=4)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)

            if resp.status_code == 200:
                data = resp.json()
                raw_models = [m.get("name", "") for m in data.get("models", [])]
                installed = [m for m in raw_models if m]

                # Check if model is present (exact match or with :latest)
                norm_target = self._normalize_model_name(model_to_check)
                norm_installed = [self._normalize_model_name(m) for m in installed]
                has_model = (model_to_check in installed) or (norm_target in norm_installed)

                if has_model:
                    msg = f"Ollama is running ({elapsed_ms}ms). Model '{model_to_check}' is ready offline."
                else:
                    msg = f"Ollama is running ({elapsed_ms}ms), but model '{model_to_check}' is not downloaded yet."

                return {
                    "is_running": True,
                    "latency_ms": elapsed_ms,
                    "models": installed,
                    "active_model": model_to_check,
                    "is_model_available": has_model,
                    "message": msg
                }
            else:
                return {
                    "is_running": False,
                    "latency_ms": 0.0,
                    "models": [],
                    "active_model": model_to_check,
                    "is_model_available": False,
                    "message": f"Ollama returned HTTP {resp.status_code}."
                }

        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            return {
                "is_running": False,
                "latency_ms": 0.0,
                "models": [],
                "active_model": model_to_check,
                "is_model_available": False,
                "message": f"Ollama is not running on {self.base_url}. Start Ollama locally to enable generation."
            }
        except Exception as e:
            return {
                "is_running": False,
                "latency_ms": 0.0,
                "models": [],
                "active_model": model_to_check,
                "is_model_available": False,
                "message": f"Ollama health check failed: {str(e)}"
            }

    def list_installed_models(self) -> List[Dict[str, Any]]:
        """Return formatted metadata for all models downloaded in Ollama."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for m in data.get("models", []):
                    size_bytes = m.get("size", 0)
                    size_gb = round(size_bytes / (1024 ** 3), 2)
                    results.append({
                        "name": m.get("name", "unknown"),
                        "size_gb": size_gb,
                        "modified_at": m.get("modified_at", ""),
                        "details": m.get("details", {})
                    })
                return results
            return []
        except Exception:
            return []

    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model exists in local Ollama storage."""
        health = self.check_health(target_model=model_name)
        return health["is_model_available"]

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Any:
        """Send prompt to local Ollama API.

        If stream=False, returns the complete generated string.
        If stream=True, yields tokens as a Generator[str, None, None].
        """
        active_model = model or self.default_model

        payload: Dict[str, Any] = {
            "model": active_model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature if temperature is not None else config.default_temperature,
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        url = f"{self.base_url}/api/generate"

        try:
            if stream:
                return self._stream_generator(url, payload, active_model)
            else:
                resp = requests.post(url, json=payload, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("response", "")
                elif resp.status_code == 404:
                    raise ModelNotFoundError(
                        f"Model '{active_model}' not found in Ollama. Run: `ollama pull {active_model}`"
                    )
                else:
                    raise OllamaClientError(
                        f"Ollama generation failed with status {resp.status_code}: {resp.text}"
                    )

        except requests.exceptions.Timeout:
            raise OllamaTimeoutError(
                f"Generation timed out after {self.timeout}s. Try a shorter story or smaller model."
            )
        except requests.exceptions.ConnectionError:
            raise OllamaConnectionError(
                f"Could not connect to Ollama at {self.base_url}. Ensure the Ollama service is running."
            )

    def _stream_generator(self, url: str, payload: Dict[str, Any], model_name: str) -> Generator[str, None, None]:
        """Generator yielding streamed text chunks from Ollama response lines."""
        try:
            with requests.post(url, json=payload, stream=True, timeout=self.timeout) as resp:
                if resp.status_code == 404:
                    raise ModelNotFoundError(
                        f"Model '{model_name}' not found in Ollama. Run: `ollama pull {model_name}`"
                    )
                if resp.status_code != 200:
                    raise OllamaClientError(f"Ollama returned HTTP {resp.status_code}")

                for line in resp.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            token = chunk.get("response", "")
                            if token:
                                yield token
                            if chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.Timeout:
            raise OllamaTimeoutError(f"Streaming inference timed out after {self.timeout}s.")
        except requests.exceptions.ConnectionError:
            raise OllamaConnectionError(f"Connection lost to Ollama during streaming at {self.base_url}.")

