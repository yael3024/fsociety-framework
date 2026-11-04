from fsociety.modules.awareness import phishing_indicators, quiz_result
from fsociety.modules.usb import inspect_usb_path


def test_usb_inspection_flags_extensions_and_hashes(tmp_path):
    (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "setup.exe").write_bytes(b"do not execute")
    result = inspect_usb_path(tmp_path)
    assert result["suspicious_count"] == 1
    assert next(item for item in result["files"] if item["relative_path"] == "setup.exe")["sha256"]


def test_offline_awareness_analysis():
    indicators = phishing_indicators("Acción urgente", "sender@example.invalid", "Confirma tu contraseña usando un enlace tinyurl")
    assert "lenguaje de urgencia o amenaza" in indicators
    assert "solicitud o mención de credenciales" in indicators
    assert quiz_result([1, 0])["score"] == 2
