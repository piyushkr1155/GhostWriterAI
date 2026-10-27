"""Tests for OllamaClient with mocked HTTP responses."""
import json
from unittest.mock import patch, MagicMock
import pytest
import requests

from src.ollama_client import (
    OllamaClient,
    OllamaClientError,
    OllamaConnectionError,
    ModelNotFoundError,
    OllamaTimeoutError
)

@pytest.fixture
def client():
    """Create a default OllamaClient instance."""
    return OllamaClient(base_url="http://localhost:11434", default_model="qwen2.5:3b", timeout=10)


def test_health_check_running_model_available(client):
    """Test health check when Ollama is online and active model is installed."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [
            {"name": "qwen2.5:3b", "size": 1900000000},
            {"name": "llama3.2:latest", "size": 2000000000}
        ]
    }

    with patch("requests.get", return_value=mock_resp):
        health = client.check_health("qwen2.5:3b")
        assert health["is_running"] is True
        assert health["is_model_available"] is True
        assert "qwen2.5:3b" in health["models"]
        assert health["latency_ms"] >= 0


def test_health_check_running_model_missing(client):
    """Test health check when Ollama is online but target model is not pulled."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [{"name": "llama3.2:latest", "size": 2000000000}]
    }

    with patch("requests.get", return_value=mock_resp):
        health = client.check_health("gemma2:27b")
        assert health["is_running"] is True
        assert health["is_model_available"] is False
        assert "not downloaded yet" in health["message"]


def test_health_check_offline(client):
    """Test health check when Ollama service is unreachable."""
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection refused")):
        health = client.check_health("qwen2.5:3b")
        assert health["is_running"] is False
        assert health["is_model_available"] is False
        assert "Start Ollama locally" in health["message"]


def test_generate_success(client):
    """Test successful generation request to Ollama /api/generate."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "response": "TITLE: Phantom Whispers\nThe floorboards creaked in rhythm with her heartbeat."
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        result = client.generate(
            prompt="Write a story",
            system_prompt="You are a horror writer",
            model="qwen2.5:3b",
            temperature=0.8
        )
        assert "Phantom Whispers" in result
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["model"] == "qwen2.5:3b"
        assert kwargs["json"]["options"]["temperature"] == 0.8


def test_generate_model_not_found(client):
    """Test that 404 response raises ModelNotFoundError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "model 'qwen2.5:3b' not found"

    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(ModelNotFoundError, match="Run: `ollama pull"):
            client.generate(prompt="Write a story", model="qwen2.5:3b")


def test_generate_connection_error(client):
    """Test that connection failure raises OllamaConnectionError."""
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError("Failed")):
        with pytest.raises(OllamaConnectionError, match="Could not connect to Ollama"):
            client.generate(prompt="Write a story")


def test_generate_timeout_error(client):
    """Test that timeout raises OllamaTimeoutError."""
    with patch("requests.post", side_effect=requests.exceptions.Timeout("Timed out")):
        with pytest.raises(OllamaTimeoutError, match="timed out after"):
            client.generate(prompt="Write a story")


def test_list_installed_models(client):
    """Test listing formatted installed models with gigabyte sizing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [
            {
                "name": "qwen2.5:3b",
                "size": 2147483648,  # exactly 2.0 GB
                "modified_at": "2026-10-25T12:00:00Z",
                "details": {"format": "gguf", "family": "qwen2"}
            }
        ]
    }

    with patch("requests.get", return_value=mock_resp):
        models = client.list_installed_models()
        assert len(models) == 1
        assert models[0]["name"] == "qwen2.5:3b"
        assert models[0]["size_gb"] == 2.0
