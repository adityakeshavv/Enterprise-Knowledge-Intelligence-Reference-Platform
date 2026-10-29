import re
from typing import Optional, Tuple
from pydantic import BaseModel

class GuardrailResult(BaseModel):
    is_safe: bool
    threat_category: Optional[str] = None
    violation_details: Optional[str] = None
    sanitized_query: str

class SecurityGuardrails:
    """
    Enterprise AI Threat Guardrail & Input Sanitization Engine.
    Implements PRD Section 23.1 threat-handling rules:
    - Prompt injection detection (direct & indirect)
    - Secret & system prompt exfiltration defense
    - Privilege escalation & authorization bypass blocking
    - Inert data sanitization for untrusted content
    """

    # Direct adversarial pattern signatures
    INJECTION_PATTERNS = [
        (r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions?", "PROMPT_INJECTION"),
        (r"disregard\s+(?:all\s+)?(?:system|guidelines|rules|prompts?)", "PROMPT_INJECTION"),
        (r"system\s+(?:prompt\s+)?override", "PROMPT_INJECTION"),
        (r"you\s+are\s+now\s+(?:in\s+)?(?:dan|developer|god|unrestricted)\s+mode", "JAILBREAK_ATTEMPT"),
        (r"bypass\s+(?:rbac|authorization|security|safety\s+filters?)", "AUTHORIZATION_BYPASS"),
        (r"(?:reveal|print|show|dump|output)\s+(?:all\s+)?(?:system\s+prompts?|instructions?|api[_\s-]?keys?|secrets?|passwords?|credentials?)", "SECRET_EXFILTRATION"),
        (r"(?:cat|echo|print)\s+(?:\.env|config\.py|settings)", "SECRET_EXFILTRATION"),
        (r"drop\s+table|delete\s+from|alter\s+table", "UNSAFE_SQL_INJECTION"),
    ]

    # Secret redaction patterns
    SECRET_REDACTION_PATTERNS = [
        (r"(Bearer\s+)[A-Za-z0-9_\-\.]{20,}", r"\1[REDACTED_TOKEN]"),
        (r"(sk-[A-Za-z0-9]{20,})", r"[REDACTED_API_KEY]"),
        (r"(password\s*[:=]\s*)[^\s,;]+", r"\1[REDACTED_PASSWORD]"),
        (r"(secret\s*[:=]\s*)[^\s,;]+", r"\1[REDACTED_SECRET]"),
    ]

    @classmethod
    def evaluate_query(cls, query_text: str, user_role: str = "Viewer") -> GuardrailResult:
        """
        Inspects incoming user queries against known adversarial threat signatures.
        """
        if not query_text or not query_text.strip():
            return GuardrailResult(is_safe=True, sanitized_query="")

        normalized = query_text.strip()

        # Check for injection / exfiltration patterns
        for pattern, threat_type in cls.INJECTION_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return GuardrailResult(
                    is_safe=False,
                    threat_category=threat_type,
                    violation_details=f"Query matches restricted adversarial signature: {threat_type}",
                    sanitized_query=normalized
                )

        # Apply secret redaction if user inadvertently pasted tokens
        sanitized = cls.redact_secrets(normalized)

        return GuardrailResult(
            is_safe=True,
            sanitized_query=sanitized
        )

    @classmethod
    def sanitize_untrusted_text(cls, text: str) -> str:
        """
        Ensures retrieved document chunks are treated strictly as passive/inert data.
        Strips or escapes pseudo-instructions embedded inside untrusted documents (PRD 23.1).
        """
        if not text:
            return ""

        # Neutralize common embedded instructions
        neutralized = re.sub(
            r"\[(?:SYSTEM|INSTRUCTION|ADMIN|DIRECTIVE):.*?\]",
            "[INERT_DOCUMENT_TEXT]",
            text,
            flags=re.IGNORECASE
        )
        return cls.redact_secrets(neutralized)

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        """Redacts credentials, tokens, and secrets from logs and outbound responses."""
        if not text:
            return ""
        result = text
        for pattern, replacement in cls.SECRET_REDACTION_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result

security_guardrails = SecurityGuardrails()
