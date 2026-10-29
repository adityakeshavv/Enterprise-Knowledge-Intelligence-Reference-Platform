import re
from typing import List, Optional
from app.orchestration.contracts import (
    IntentCategory, IntentClassificationResult, ExecutionMode,
    QueryUnderstandingResult
)
from app.orchestration.taxonomy import intent_taxonomy

class IntentClassificationAgent:
    """Stage 2: Dedicated intent-classification component mapping understood queries
    to configurable intent categories with uncertainty scoring and threshold-gated fallbacks.
    """

    def __init__(self, taxonomy=intent_taxonomy):
        self.taxonomy = taxonomy

    def classify(self, understanding: QueryUnderstandingResult) -> IntentClassificationResult:
        query_text = understanding.normalized_query
        q_lower = query_text.lower()

        scores = {}
        for definition in self.taxonomy.list_definitions():
            score = 0.0
            # 1. Regex pattern matching
            for pattern in definition.regex_patterns:
                if re.search(pattern, q_lower):
                    score += 0.45

            # 2. Keyword match density
            matched_keywords = [kw for kw in definition.signal_keywords if kw in q_lower]
            if matched_keywords:
                score += min(0.55, len(matched_keywords) * 0.15)

            scores[definition.category] = round(min(1.0, score), 3)

        # Sort intents by confidence score
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_score = sorted_intents[0]

        # Check for cross-source combination signals
        has_sql_signals = scores.get(IntentCategory.STRUCTURED_TELEMETRY, 0.0) >= 0.35
        has_doc_signals = scores.get(IntentCategory.PROCEDURAL_GUIDANCE, 0.0) >= 0.35

        if has_sql_signals and has_doc_signals:
            top_intent = IntentCategory.CROSS_SOURCE_INVESTIGATION
            top_score = max(top_score, 0.92)

        definition = self.taxonomy.get_definition(top_intent)
        threshold = definition.confidence_threshold if definition else 0.50

        # Secondary intents
        secondary_intents: List[IntentCategory] = []
        for cat, sc in sorted_intents[1:]:
            if sc >= 0.40 and cat != top_intent:
                secondary_intents.append(cat)

        # Fallback check
        fallback_triggered = False
        fallback_reason = None

        if top_score < threshold:
            fallback_triggered = True
            fallback_reason = (
                f"Classification confidence ({top_score:.2f}) fell below threshold ({threshold:.2f}). "
                "Triggering conservative cross-source retrieval fallback."
            )
            # Safe default fallback
            top_intent = IntentCategory.CROSS_SOURCE_INVESTIGATION
            top_score = threshold

        required_caps = list(definition.required_capabilities) if definition else ["structured_query", "unstructured_retrieval"]
        target_sources = list(definition.target_sources) if definition else ["SQL_DATABASE", "DOCUMENT_STORE"]
        strategy = definition.processing_strategy if definition else ExecutionMode.PARALLEL

        # Aggregate secondary intent capabilities and target sources
        for sec in secondary_intents:
            sec_def = self.taxonomy.get_definition(sec)
            if sec_def:
                for cap in sec_def.required_capabilities:
                    if cap not in required_caps:
                        required_caps.append(cap)
                for src in sec_def.target_sources:
                    if src not in target_sources:
                        target_sources.append(src)
                if len(target_sources) > 1:
                    strategy = ExecutionMode.PARALLEL

        return IntentClassificationResult(
            predicted_intent=top_intent,
            secondary_intents=secondary_intents,
            confidence=top_score,
            uncertainty=round(1.0 - top_score, 3),
            required_capabilities=required_caps,
            target_source_types=target_sources,
            processing_strategy=strategy,
            fallback_triggered=fallback_triggered,
            fallback_reason=fallback_reason
        )

intent_classification_agent = IntentClassificationAgent()
