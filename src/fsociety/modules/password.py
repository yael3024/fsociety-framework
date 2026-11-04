"""Local-only password strength auditing; input is never logged or retained."""

import math
import re

COMMON_PATTERNS = ("password", "qwerty", "letmein", "admin", "welcome", "123456", "iloveyou")


def audit_password(password: str) -> dict:
    if not isinstance(password, str):
        raise TypeError("La contraseña debe ser texto.")
    length = len(password)
    classes = {"lowercase": any(c.islower() for c in password), "uppercase": any(c.isupper() for c in password), "digits": any(c.isdigit() for c in password), "symbols": any(not c.isalnum() and not c.isspace() for c in password), "spaces": any(c.isspace() for c in password)}
    lowered = password.lower()
    patterns = []
    if any(pattern in lowered for pattern in COMMON_PATTERNS):
        patterns.append("common_word_or_sequence")
    if re.search(r"(.)\1{2,}", password):
        patterns.append("repeated_characters")
    if any(sequence in lowered for sequence in ("abcd", "qwerty", "asdf", "1234", "4321")):
        patterns.append("keyboard_or_sequential_pattern")
    pool = sum((26 if classes["lowercase"] else 0, 26 if classes["uppercase"] else 0, 10 if classes["digits"] else 0, 33 if classes["symbols"] else 0, 1 if classes["spaces"] else 0))
    entropy = round(length * math.log2(pool), 1) if pool else 0.0
    score = 0 if length < 8 else 1 if length < 12 else 2 if length < 16 else 3
    score += min(sum(classes[key] for key in ("lowercase", "uppercase", "digits", "symbols")), 3)
    score -= min(len(patterns), 2)
    score = max(0, min(4, score))
    recommendations = []
    if length < 14:
        recommendations.append("Usa una frase de contraseña de al menos 14 caracteres.")
    if sum(classes[key] for key in ("lowercase", "uppercase", "digits", "symbols")) < 3:
        recommendations.append("Combina varios tipos de caracteres o usa palabras aleatorias largas.")
    if patterns:
        recommendations.append("Evita palabras comunes, secuencias y caracteres repetidos.")
    if not recommendations:
        recommendations.append("Mantén esta contraseña única y usa un gestor de contraseñas.")
    return {"length": length, "character_classes": classes, "patterns": patterns, "estimated_entropy_bits": entropy, "score": score, "rating": ("muy débil", "débil", "moderada", "fuerte", "muy fuerte")[score], "recommendations": recommendations}
