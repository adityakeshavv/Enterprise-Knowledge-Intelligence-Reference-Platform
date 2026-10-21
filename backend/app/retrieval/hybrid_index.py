import re
import math
from typing import List, Dict, Any, Tuple, Optional
from rank_bm25 import BM25Okapi
from app.ingestion.models import DocumentChunk

def _tokenize(text: str) -> List[str]:
    """Tokenize query and documents for BM25 lexical matching."""
    # Split on non-alphanumeric, keeping dashes/underscores for part numbers like AFD-SEAL-882
    tokens = re.findall(r"[A-Za-z0-9_\-\.]+", text.lower())
    return [t for t in tokens if len(t) > 1]

class HybridDocumentIndex:
    """Hybrid Retrieval Index combining BM25 keyword matching with dense lexical-semantic scoring."""

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.chunk_ids: List[str] = []
        self.bm25: Optional[BM25Okapi] = None
        self.tokenized_corpus: List[List[str]] = []

    def clear(self):
        self.chunks.clear()
        self.chunk_ids.clear()
        self.bm25 = None
        self.tokenized_corpus.clear()

    def add_chunks(self, new_chunks: List[DocumentChunk]):
        for chunk in new_chunks:
            if chunk.chunk_id not in self.chunk_ids:
                self.chunks.append(chunk)
                self.chunk_ids.append(chunk.chunk_id)
        self._rebuild_bm25()

    def _rebuild_bm25(self):
        if not self.chunks:
            self.bm25 = None
            self.tokenized_corpus = []
            return
        self.tokenized_corpus = [_tokenize(chunk.text) for chunk in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5  # 0.5 balanced weight between BM25 and semantic lexical match
    ) -> List[Tuple[DocumentChunk, float]]:
        if not self.chunks or self.bm25 is None:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        # 1. BM25 Scores (clamped to non-negative)
        bm25_raw_scores = self.bm25.get_scores(query_tokens)
        max_bm25 = max(bm25_raw_scores) if max(bm25_raw_scores) > 0 else 0.0
        normalized_bm25 = [max(0.0, s / max_bm25) if max_bm25 > 0 else 0.0 for s in bm25_raw_scores]

        # 2. Semantic Token Overlap & Fuzzy Jaccard
        query_set = set(query_tokens)
        semantic_scores = []
        for doc_tokens in self.tokenized_corpus:
            doc_set = set(doc_tokens)
            intersection = query_set.intersection(doc_set)
            jaccard = len(intersection) / len(query_set.union(doc_set)) if query_set or doc_set else 0.0
            # Boost exact substring matches
            exact_bonus = 0.5 if any(t in doc_tokens for t in query_tokens) else 0.0
            semantic_scores.append(min(1.0, jaccard * 2.0 + exact_bonus))

        # 3. Combine with Filter Enforcement
        results: List[Tuple[DocumentChunk, float]] = []
        for idx, chunk in enumerate(self.chunks):
            # Apply metadata filters
            if filters:
                allowed = True
                meta = chunk.metadata
                for f_key, f_val in filters.items():
                    if f_key == "department" and meta.get("department") and meta.get("department") != f_val:
                        allowed = False
                        break
                    if f_key == "max_classification":
                        # Clearance check: Public < Internal < Confidential < Restricted
                        hierarchy = {"Public": 1, "Internal": 2, "Confidential": 3, "Restricted": 4}
                        doc_level = hierarchy.get(meta.get("classification", "Internal"), 2)
                        user_level = hierarchy.get(f_val, 4)
                        if doc_level > user_level:
                            allowed = False
                            break
                if not allowed:
                    continue

            combined_score = (1 - alpha) * normalized_bm25[idx] + alpha * semantic_scores[idx]
            if combined_score > 0.0 or semantic_scores[idx] > 0.0:
                results.append((chunk, max(combined_score, semantic_scores[idx])))

        # Sort descending by score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

# Global singleton hybrid index instance
hybrid_index = HybridDocumentIndex()
