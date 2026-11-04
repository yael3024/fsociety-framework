"""Offline security awareness exercises. No messages are sent and no secrets collected."""

from __future__ import annotations

EXAMPLE_EMAIL = {"subject": "Acción urgente: verifica tu cuenta", "sender": "security-update@example.invalid", "body": "Tu cuenta será suspendida hoy. Abre el enlace acortado y confirma tu contraseña.", "indicators": ["urgencia artificial", "dominio de remitente no verificable", "solicitud de credenciales", "enlace acortado"]}
QUIZ = [{"question": "¿Qué debes hacer ante un enlace inesperado que solicita iniciar sesión?", "options": ["Abrirlo de inmediato", "Verificar el dominio por un canal conocido", "Responder con tu contraseña"], "answer": 1, "explanation": "Verifica por un canal confiable y navega al sitio escribiendo su dirección."}, {"question": "¿Cuál es una señal frecuente de phishing?", "options": ["Presión urgente y remitente inusual", "Actualización esperada desde el portal habitual", "Mensaje sin enlaces"], "answer": 0, "explanation": "La urgencia y las direcciones inesperadas son señales para revisar."}]


def phishing_indicators(subject: str, sender: str, body: str) -> list[str]:
    text = f"{subject} {sender} {body}".lower()
    indicators = []
    if any(word in text for word in ("urgente", "inmediato", "suspend", "último aviso", "verify now")):
        indicators.append("lenguaje de urgencia o amenaza")
    if any(word in text for word in ("contraseña", "password", "credenciales", "iniciar sesión", "login")):
        indicators.append("solicitud o mención de credenciales")
    if any(word in text for word in ("bit.ly", "tinyurl", "t.co", "acortado")):
        indicators.append("enlace acortado")
    if "@" not in sender or sender.endswith(".invalid"):
        indicators.append("remitente no verificable")
    return indicators


def quiz_result(answers: list[int]) -> dict:
    if len(answers) != len(QUIZ) or any(not isinstance(answer, int) or answer not in range(3) for answer in answers):
        raise ValueError("Se requiere una respuesta válida para cada pregunta.")
    score = sum(answer == item["answer"] for answer, item in zip(answers, QUIZ))
    return {"score": score, "total": len(QUIZ), "percentage": round(score / len(QUIZ) * 100), "feedback": [item["explanation"] for item in QUIZ]}
