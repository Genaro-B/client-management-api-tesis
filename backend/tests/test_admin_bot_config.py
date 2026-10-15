"""Tests de los getters de configuración del asistente administrativo.

Verifica el patrón "lectura por llamada" (como _bcrypt_rounds): cada getter
lee la variable de entorno en el momento y aplica un default razonable.
"""
import src.core.config as config


def test_admin_bot_brain_default_es_classifier(monkeypatch):
    monkeypatch.delenv("ADMIN_BOT_BRAIN", raising=False)
    assert config.get_admin_bot_brain() == "classifier"


def test_admin_bot_brain_lee_entorno_y_normaliza(monkeypatch):
    monkeypatch.setenv("ADMIN_BOT_BRAIN", "  DETERMINISTIC  ")
    assert config.get_admin_bot_brain() == "deterministic"


def test_admin_bot_nlu_threshold_default(monkeypatch):
    monkeypatch.delenv("ADMIN_BOT_NLU_THRESHOLD", raising=False)
    assert config.get_admin_bot_nlu_threshold() == 0.55


def test_admin_bot_nlu_threshold_lee_entorno(monkeypatch):
    monkeypatch.setenv("ADMIN_BOT_NLU_THRESHOLD", "0.8")
    assert config.get_admin_bot_nlu_threshold() == 0.8


def test_ollama_url_default(monkeypatch):
    monkeypatch.delenv("OLLAMA_URL", raising=False)
    assert config.get_ollama_url() == "http://localhost:11434"


def test_ollama_url_lee_entorno(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://otro-host:1234")
    assert config.get_ollama_url() == "http://otro-host:1234"


def test_ollama_model_default(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    assert config.get_ollama_model() == "qwen2.5:3b"


def test_ollama_model_lee_entorno(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "llama3:8b")
    assert config.get_ollama_model() == "llama3:8b"


def test_ollama_timeout_default(monkeypatch):
    monkeypatch.delenv("OLLAMA_TIMEOUT_SECONDS", raising=False)
    assert config.get_ollama_timeout_seconds() == 30


def test_ollama_timeout_lee_entorno(monkeypatch):
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "5")
    assert config.get_ollama_timeout_seconds() == 5
