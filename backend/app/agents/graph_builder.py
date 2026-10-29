import re
from typing import List, Optional
from app.schemas.query import (
    CitationItem, ConflictItem, FindingItem, FactClassification,
    EvidenceGraph, EvidenceGraphNode, EvidenceGraphEdge
)

class EvidenceGraphBuilder:
    """Builds interactive visual relationship graphs mapping enterprise queries,
    retrieved telemetry and document sources, verified claims, and operational discrepancies.
    """

    def build_graph(
        self,
        query_text: str,
        findings: List[FindingItem],
        citations: List[CitationItem],
        conflicts: List[ConflictItem],
        is_abstained: bool = False
    ) -> EvidenceGraph:
        """Constructs an EvidenceGraph instance linking nodes and directed edges."""
        nodes: List[EvidenceGraphNode] = []
        edges: List[EvidenceGraphEdge] = []

        # 1. Root Query Node
        query_label = query_text if len(query_text) <= 50 else f"{query_text[:47]}..."
        nodes.append(
            EvidenceGraphNode(
                id="node_query",
                label=query_label,
                node_type="query",
                category="root",
                metadata={"full_text": query_text, "is_abstained": is_abstained}
            )
        )

        if is_abstained:
            # If abstained, add boundary node and single edge
            nodes.append(
                EvidenceGraphNode(
                    id="node_abstention_boundary",
                    label="Zero-Hallucination Information Boundary",
                    node_type="conflict",
                    category="boundary",
                    metadata={"status": "abstained", "reason": "Query outside indexed corpus"}
                )
            )
            edges.append(
                EvidenceGraphEdge(
                    source="node_query",
                    target="node_abstention_boundary",
                    relation="BLOCKED_BY",
                    is_conflict=True
                )
            )
            return EvidenceGraph(nodes=nodes, edges=edges)

        # 2. Source Nodes (SQL & Document Citations)
        source_id_map = {}
        for cit in citations:
            src_node_id = f"node_src_{cit.citation_id}"
            source_id_map[cit.citation_id] = src_node_id

            node_type = "sql_source" if cit.source_type == "SQL_QUERY" else "doc_source"
            category = "telemetry" if cit.source_type == "SQL_QUERY" else "sop"
            ref_label = cit.reference.split("/")[-1].split("\\")[-1]
            if len(ref_label) > 28:
                ref_label = f"{ref_label[:25]}..."
            label = f"[{cit.citation_id}] {ref_label}"

            nodes.append(
                EvidenceGraphNode(
                    id=src_node_id,
                    label=label,
                    node_type=node_type,
                    category=category,
                    metadata={
                        "citation_id": cit.citation_id,
                        "reference": cit.reference,
                        "title": cit.title,
                        "snippet": cit.snippet,
                        "source_type": cit.source_type
                    }
                )
            )

            # Edge from Query to Source (retrieval path)
            edges.append(
                EvidenceGraphEdge(
                    source="node_query",
                    target=src_node_id,
                    relation="RETRIEVED",
                    is_conflict=False
                )
            )

        # 3. Finding Nodes (Verified Facts & Analytical Inferences)
        fact_node_ids = []
        for idx, finding in enumerate(findings):
            find_node_id = f"node_find_{idx+1}"
            category = "fact" if finding.classification == FactClassification.VERIFIED_FACT else "inference"
            
            clean_stmt = re.sub(r"\[[A-Za-z0-9_\-\.]+\]", "", finding.statement).strip()
            label = clean_stmt if len(clean_stmt) <= 45 else f"{clean_stmt[:42]}..."

            nodes.append(
                EvidenceGraphNode(
                    id=find_node_id,
                    label=label,
                    node_type="finding",
                    category=category,
                    metadata={
                        "statement": finding.statement,
                        "classification": finding.classification.value,
                        "citation_ids": finding.citation_ids,
                        "confidence": finding.confidence
                    }
                )
            )

            if category == "fact":
                fact_node_ids.append(find_node_id)

            # Link Source -> Finding if citation tags present
            linked_source = False
            for cid in finding.citation_ids:
                if cid in source_id_map:
                    edges.append(
                        EvidenceGraphEdge(
                            source=source_id_map[cid],
                            target=find_node_id,
                            relation="GROUNDS",
                            is_conflict=False
                        )
                    )
                    linked_source = True

            # If no direct citation was tagged or for inferences, link from Root Query or a Fact
            if not linked_source:
                if category == "inference" and fact_node_ids:
                    # Link previous fact to this inference
                    edges.append(
                        EvidenceGraphEdge(
                            source=fact_node_ids[0],
                            target=find_node_id,
                            relation="DERIVED_FROM",
                            is_conflict=False
                        )
                    )
                else:
                    edges.append(
                        EvidenceGraphEdge(
                            source="node_query",
                            target=find_node_id,
                            relation="PRODUCED",
                            is_conflict=False
                        )
                    )

        # 4. Conflict Nodes (Contradictions & Discrepancies)
        for conf in conflicts:
            conf_node_id = f"node_conf_{conf.conflict_id}"
            nodes.append(
                EvidenceGraphNode(
                    id=conf_node_id,
                    label=f"[{conf.conflict_id}] {conf.title[:38]}...",
                    node_type="conflict",
                    category="discrepancy",
                    metadata={
                        "conflict_id": conf.conflict_id,
                        "title": conf.title,
                        "description": conf.description,
                        "source_a": conf.source_a,
                        "source_b": conf.source_b,
                        "recommendation": conf.recommendation
                    }
                )
            )

            # Connect source nodes or findings to this conflict
            # If we have both SQL and Doc citations, connect them to show the tension
            connected_conflict = False
            for cit in citations:
                if cit.citation_id in source_id_map:
                    edges.append(
                        EvidenceGraphEdge(
                            source=source_id_map[cit.citation_id],
                            target=conf_node_id,
                            relation="CONTRADICTS",
                            is_conflict=True
                        )
                    )
                    connected_conflict = True

            if not connected_conflict:
                edges.append(
                    EvidenceGraphEdge(
                        source="node_query",
                        target=conf_node_id,
                        relation="SURFACED",
                        is_conflict=True
                    )
                )

        return EvidenceGraph(nodes=nodes, edges=edges)

evidence_graph_builder = EvidenceGraphBuilder()
