import React, { useState, useMemo, useRef, useId } from "react";
import type { EvidenceGraph, EvidenceGraphNode, CitationItem } from "../types";
import {
  FileText,
  HelpCircle,
  Maximize2,
  Minimize2,
  RotateCcw,
  Layers
} from "lucide-react";

interface EvidenceGraphProps {
  graph?: EvidenceGraph;
  citations: CitationItem[];
  onOpenCitation: (citation: CitationItem) => void;
  onSelectConflict?: (conflictId: string) => void;
}

type GraphNodeLayout = { x: number; y: number; width: number; height: number; lines: string[] };

const wrapLabel = (label: string, maxChars: number, maxLines = 4) => {
  const words = (label || "Untitled evidence").split(/\s+/);
  const lines: string[] = [];
  let line = "";
  words.forEach((word) => {
    if (!line && word.length > maxChars) {
      for (let i = 0; i < word.length; i += maxChars) lines.push(word.slice(i, i + maxChars));
      return;
    }
    const next = line ? `${line} ${word}` : word;
    if (next.length > maxChars && line) { lines.push(line); line = word; }
    else line = next;
  });
  if (line) lines.push(line);
  if (lines.length > maxLines) {
    lines.length = maxLines;
    lines[maxLines - 1] = `${lines[maxLines - 1].replace(/[.]+$/, "")}...`;
  }
  return lines.length ? lines : ["Untitled evidence"];
};

export const EvidenceGraphView: React.FC<EvidenceGraphProps> = ({
  graph,
  citations,
  onOpenCitation,
  onSelectConflict
}) => {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>("ALL");
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const canvasRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<{ pointerId: number; x: number; y: number; left: number; top: number } | null>(null);
  const markerPrefix = useId().replace(/[^a-zA-Z0-9_-]/g, "");
  const markerNormal = `arrowhead-normal-${markerPrefix}`;
  const markerConflict = `arrowhead-conflict-${markerPrefix}`;
  const markerActive = `arrowhead-active-${markerPrefix}`;

  const graphNodes = graph?.nodes ?? [];
  const graphEdges = graph?.edges ?? [];

  // Filter nodes according to active filter
  const visibleNodes = useMemo(() => {
    if (filterType === "ALL") return graphNodes;
    if (filterType === "FACTS") return graphNodes.filter(n => n.node_type === "query" || (n.node_type === "finding" && n.category?.toLowerCase().includes("fact")));
    if (filterType === "SQL") return graphNodes.filter(n => n.node_type === "query" || n.node_type === "sql_source");
    if (filterType === "DOCS") return graphNodes.filter(n => n.node_type === "query" || n.node_type === "doc_source");
    if (filterType === "CONFLICTS") return graphNodes.filter(n => n.node_type === "query" || n.node_type === "conflict" || n.node_type === "sql_source" || n.node_type === "doc_source");
    return graphNodes;
  }, [graphNodes, filterType]);

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map(n => n.id)), [visibleNodes]);

  const visibleEdges = useMemo(() => {
    return graphEdges.filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target));
  }, [graphEdges, visibleNodeIds]);

  // Lay out every graph from its actual contents: labels wrap, columns grow, and
  // connected nodes are ordered together to reduce edge crossings.
  const graphLayout = useMemo(() => {
    const rankOf = (node: EvidenceGraphNode) => ({ query: 0, sql_source: 1, doc_source: 1, finding: 2, conflict: 3 }[node.node_type] ?? 2);
    const nodeById = new Map(visibleNodes.map(node => [node.id, node]));
    const ranks = new Map(visibleNodes.map(node => [node.id, rankOf(node)]));
    // Promote downstream nodes when the data contains relationships beyond
    // the usual query -> source -> finding flow (for example derived findings).
    for (let pass = 0; pass < visibleNodes.length; pass += 1) {
      visibleEdges.forEach(edge => {
        const sourceRank = ranks.get(edge.source);
        const target = nodeById.get(edge.target);
        if (sourceRank !== undefined && target && target.node_type !== "query") {
          ranks.set(target.id, Math.max(ranks.get(target.id) ?? 0, Math.min(visibleNodes.length, sourceRank + 1)));
        }
      });
    }
    const maxRank = Math.max(0, ...ranks.values());
    const layers: EvidenceGraphNode[][] = Array.from({ length: maxRank + 1 }, () => []);
    visibleNodes.forEach(node => layers[ranks.get(node.id) ?? 0].push(node));
    const ordered: EvidenceGraphNode[][] = [];
    const layerIndexes: Map<string, number>[] = [];
    layers.forEach((layer, rank) => {
      if (rank > 0) {
        const score = (node: EvidenceGraphNode) => {
          const neighbors = visibleEdges.filter(edge => edge.target === node.id && (ranks.get(edge.source) ?? -1) < rank)
            .map(edge => {
              const sourceRank = ranks.get(edge.source);
              const sourceIndex = sourceRank === undefined ? undefined : layerIndexes[sourceRank]?.get(edge.source);
              const sourceLayerSize = sourceRank === undefined ? 0 : ordered[sourceRank]?.length ?? 0;
              return sourceIndex === undefined || sourceLayerSize === 0 ? undefined : (sourceIndex + 0.5) / sourceLayerSize;
            }).filter((value): value is number => value !== undefined);
          return neighbors.length ? neighbors.reduce((sum, value) => sum + value, 0) / neighbors.length : Number.MAX_SAFE_INTEGER;
        };
        layer.sort((a, b) => score(a) - score(b));
      }
      ordered.push(layer);
      layerIndexes.push(new Map(layer.map((node, index) => [node.id, index])));
    });

    const layouts: Record<string, GraphNodeLayout> = {};
    const columnWidths = ordered.map(layer => Math.max(210, ...layer.map(node => Math.min(310, Math.max(210, Math.min((node.label?.length ?? 0) * 6.7 + 36, 310))))));
    const columnX: number[] = [];
    let cursorX = 32;
    columnWidths.forEach((width, index) => { columnX[index] = cursorX; cursorX += width + 108; });
    const layerHeights = ordered.map(layer => layer.reduce((sum, node) => {
      const width = Math.min(310, Math.max(210, Math.min((node.label?.length ?? 0) * 6.7 + 36, 310)));
      const lines = wrapLabel(node.label, Math.max(22, Math.floor((width - 32) / 7.1)));
      return sum + Math.max(58, lines.length * 16 + 30) + 30;
    }, 0));
    const height = Math.max(480, ...layerHeights) + 44;
    ordered.forEach((layer, rank) => {
      const contentHeight = layerHeights[rank];
      let y = 22 + (height - 44 - contentHeight) / 2;
      layer.forEach(node => {
        const width = Math.min(310, Math.max(210, Math.min((node.label?.length ?? 0) * 6.7 + 36, 310)));
        const lines = wrapLabel(node.label, Math.max(22, Math.floor((width - 32) / 7.1)));
        const nodeHeight = Math.max(58, lines.length * 16 + 30);
        layouts[node.id] = { x: columnX[rank], y: y + nodeHeight / 2, width, height: nodeHeight, lines };
        y += nodeHeight + 30;
      });
    });
    return { nodes: layouts, width: Math.max(940, cursorX - 76), height };
  }, [visibleNodes, visibleEdges]);

  // Handle clicking a node
  const handleNodeClick = (node: EvidenceGraphNode) => {
    setSelectedNodeId(node.id);

    if (node.node_type === "sql_source" || node.node_type === "doc_source") {
      const citId = node.metadata?.citation_id;
      const matched = citations.find(c => c.citation_id === citId);
      if (matched) {
        onOpenCitation(matched);
      }
    } else if (node.node_type === "conflict" && onSelectConflict) {
      const confId = node.metadata?.conflict_id;
      if (confId) onSelectConflict(confId);
    }
  };

  const selectedNode = useMemo(() => {
    return graphNodes.find(n => n.id === selectedNodeId) || null;
  }, [graphNodes, selectedNodeId]);

  if (graphNodes.length === 0) {
    return (
      <div className="graph-empty-state">
        <HelpCircle size={28} className="text-muted" />
        <p>No relational evidence graph is available for this response.</p>
      </div>
    );
  }

  return (
    <div className="evidence-graph-container">
      {/* Top Graph Controls Bar */}
      <div className="graph-toolbar">
        <div className="graph-filters">
          <span className="filter-title"><Layers size={14} /> Filter Layer:</span>
          {[
            { id: "ALL", label: "All Nodes" },
            { id: "FACTS", label: "Verified Facts" },
            { id: "SQL", label: "SQL Telemetry" },
            { id: "DOCS", label: "SOP Manuals" },
            { id: "CONFLICTS", label: "Discrepancies" }
          ].map(f => (
            <button
              key={f.id}
              className={`filter-pill ${filterType === f.id ? "active" : ""}`}
              onClick={() => setFilterType(f.id)}
              aria-pressed={filterType === f.id}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className="graph-zoom-actions">
          <button
            className="graph-btn"
            onClick={() => setZoomLevel(prev => Math.min(prev + 0.15, 1.6))}
            title="Zoom In"
            aria-label="Zoom in on evidence graph"
          >
            <Maximize2 size={13} />
          </button>
          <button
            className="graph-btn"
            onClick={() => setZoomLevel(prev => Math.max(prev - 0.15, 0.7))}
            title="Zoom Out"
            aria-label="Zoom out on evidence graph"
          >
            <Minimize2 size={13} />
          </button>
          <button
            className="graph-btn"
            onClick={() => { setZoomLevel(1); setSelectedNodeId(null); canvasRef.current?.scrollTo({ left: 0, top: 0, behavior: "smooth" }); }}
            title="Reset View"
            aria-label="Reset evidence graph view"
          >
            <RotateCcw size={13} />
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div ref={canvasRef} className="graph-canvas-wrapper" role="group" aria-label="Evidence graph. Drag the background to pan; use the controls to zoom."
        onPointerDown={(event) => {
          if ((event.target as Element).closest(".graph-node-group")) return;
          dragRef.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY, left: event.currentTarget.scrollLeft, top: event.currentTarget.scrollTop };
          event.currentTarget.setPointerCapture(event.pointerId);
        }}
        onPointerMove={(event) => {
          const drag = dragRef.current;
          if (drag?.pointerId === event.pointerId) {
            event.currentTarget.scrollLeft = drag.left - (event.clientX - drag.x);
            event.currentTarget.scrollTop = drag.top - (event.clientY - drag.y);
          }
        }}
        onPointerUp={() => { dragRef.current = null; }}
        onPointerCancel={() => { dragRef.current = null; }}>
        <svg
          className="evidence-graph-svg"
          role="group"
          viewBox={`0 0 ${graphLayout.width} ${graphLayout.height}`}
          width={graphLayout.width * zoomLevel}
          height={graphLayout.height * zoomLevel}
          style={{
            maxWidth: "none",
            flex: "none",
            transition: "width 0.2s ease, height 0.2s ease"
          }}
        >
          <defs>
            {/* Arrowhead marker */}
            <marker
              id={markerNormal}
              markerWidth="8"
              markerHeight="6"
              refX="8"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#64748b" />
            </marker>
            <marker
              id={markerConflict}
              markerWidth="9"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 9 3.5, 0 7" fill="#f59e0b" />
            </marker>
            <marker
              id={markerActive}
              markerWidth="8"
              markerHeight="6"
              refX="8"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />
            </marker>
          </defs>

          {/* Render Directed Edges */}
          {visibleEdges.map((edge, idx) => {
            const p1 = graphLayout.nodes[edge.source];
            const p2 = graphLayout.nodes[edge.target];
            if (!p1 || !p2) return null;

            const isHighlighted = selectedNodeId === edge.source || selectedNodeId === edge.target;
            const isConflict = edge.is_conflict;

            // Compute curved bezier path
            const startX = p1.x + p1.width;
            const endX = p2.x;
            const midX = (startX + endX) / 2;
            const pathData = `M ${startX} ${p1.y} C ${midX} ${p1.y}, ${midX} ${p2.y}, ${endX} ${p2.y}`;

            const strokeColor = isConflict
              ? "#f59e0b"
              : isHighlighted
              ? "#38bdf8"
              : "#475569";
            
            const strokeWidth = isConflict ? 2.5 : isHighlighted ? 2.2 : 1.5;
            const strokeDash = isConflict ? "5,4" : "none";
            const markerEnd = isConflict
              ? `url(#${markerConflict})`
              : isHighlighted
              ? `url(#${markerActive})`
              : `url(#${markerNormal})`;

            return (
              <g key={`edge-${idx}`} className="edge-group">
                <path
                  d={pathData}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDash}
                  markerEnd={markerEnd}
                  opacity={isHighlighted || isConflict ? 0.95 : 0.65}
                />
                {/* Edge relation label */}
                {visibleEdges.length <= 7 && <text
                  x={midX}
                  y={(p1.y + p2.y) / 2 - 7 + (idx % 2 ? 10 : 0)}
                  fill={isConflict ? "#fbbf24" : "#94a3b8"}
                  fontSize="9"
                  textAnchor="middle"
                  className="edge-label"
                >
                  {edge.relation}
                </text>}
                <title>{edge.relation}</title>
              </g>
            );
          })}

          {/* Render Nodes */}
          {visibleNodes.map((node) => {
            const pos = graphLayout.nodes[node.id];
            if (!pos) return null;

            const isSelected = selectedNodeId === node.id;
            const isQuery = node.node_type === "query";
            const isSQL = node.node_type === "sql_source";
            const isDoc = node.node_type === "doc_source";
            const isFinding = node.node_type === "finding";
            const isFact = isFinding && node.category?.toLowerCase().includes("fact");
            const isConflict = node.node_type === "conflict";

            // Colors
            let fillBg = "#1e293b";
            let strokeColor = "#334155";
            let textColor = "#f1f5f9";

            if (isQuery) {
              fillBg = "#0284c7";
              strokeColor = "#38bdf8";
            } else if (isSQL) {
              fillBg = "rgba(37, 99, 235, 0.25)";
              strokeColor = "#3b82f6";
            } else if (isDoc) {
              fillBg = "rgba(217, 119, 6, 0.22)";
              strokeColor = "#f59e0b";
            } else if (isFact) {
              fillBg = "rgba(16, 185, 129, 0.2)";
              strokeColor = "#10b981";
            } else if (isFinding && !isFact) {
              fillBg = "rgba(147, 51, 234, 0.2)";
              strokeColor = "#a855f7";
            } else if (isConflict) {
              fillBg = "rgba(239, 68, 68, 0.25)";
              strokeColor = "#ef4444";
            }

            if (isSelected) {
              strokeColor = "#ffffff";
            }

            const boxWidth = pos.width;
            const boxHeight = pos.height;

            return (
              <g
                key={node.id}
                className="graph-node-group"
                transform={`translate(${pos.x}, ${pos.y - boxHeight / 2})`}
              onClick={() => handleNodeClick(node)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  handleNodeClick(node);
                }
              }}
              role="button"
              tabIndex={0}
              aria-label={`${node.node_type}: ${node.label}`}
              aria-pressed={isSelected}
                style={{ cursor: "pointer" }}
              >
                {/* Node Box */}
                <rect
                  width={boxWidth}
                  height={boxHeight}
                  rx="6"
                  fill={fillBg}
                  stroke={strokeColor}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  className="graph-node-rect"
                />

                <title>{node.label}</title>
                <text x={boxWidth / 2} y={boxHeight / 2 - ((pos.lines.length - 1) * 8)} textAnchor="middle"
                  fill={textColor} fontSize="12" fontWeight={isSelected || isQuery ? "bold" : "normal"} className="graph-node-text">
                  {pos.lines.map((line, lineIndex) => <tspan key={`${node.id}-line-${lineIndex}`} x={boxWidth / 2} dy={lineIndex === 0 ? 0 : 16}>{line}</tspan>)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected Node Details Card */}
      {selectedNode && (
        <div className="graph-node-details">
          <div className="details-header">
            <span className="node-type-badge">{selectedNode.node_type.toUpperCase()}</span>
            <h4 className="node-title">{selectedNode.label}</h4>
          </div>
          <p className="node-desc">
            {selectedNode.metadata?.statement ||
              selectedNode.metadata?.snippet ||
              selectedNode.metadata?.description ||
              selectedNode.metadata?.full_text ||
              "Connected provenance entity"}
          </p>
          {(selectedNode.node_type === "sql_source" || selectedNode.node_type === "doc_source") && (
            <button
              className="btn-inspect-evidence"
              onClick={() => handleNodeClick(selectedNode)}
            >
              <FileText size={12} /> Inspect Provenance Proof
            </button>
          )}
        </div>
      )}

      {/* Graph Legend */}
      <div className="graph-legend">
        <span className="legend-item"><span className="legend-dot bg-blue" /> User Query</span>
        <span className="legend-item"><span className="legend-dot bg-indigo" /> SQL Telemetry</span>
        <span className="legend-item"><span className="legend-dot bg-amber" /> SOP Document</span>
        <span className="legend-item"><span className="legend-dot bg-emerald" /> Verified Fact</span>
        <span className="legend-item"><span className="legend-dot bg-purple" /> Inference</span>
        <span className="legend-item"><span className="legend-dot bg-red" /> Conflict Alert</span>
        <span className="legend-item"><span className="legend-dot bg-amber" /> Dashed link: contradiction</span>
      </div>
    </div>
  );
};
