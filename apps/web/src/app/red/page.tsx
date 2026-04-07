"use client";

import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import dynamic from "next/dynamic";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <div className="w-12 h-12 border-4 border-neutral-600 border-t-white rounded-full animate-spin"></div>
    </div>
  ),
});

interface Node {
  id: number;
  label: string;
  type: string;
  nit: string;
  riesgo_max: number;
  sancionado: boolean;
  val: number;
  x?: number;
  y?: number;
  [key: string]: any;
}

interface Link {
  source: number;
  target: number;
  num_contratos: number;
  valor_total: number;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function RedPage() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightNode, setHighlightNode] = useState<number | null>(null);
  const [highlightLinks, setHighlightLinks] = useState<Set<number>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");
  const fgRef = useRef<any>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  const API_BASE = "http://localhost:8000";

  // Fetch data
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/red/topologia`);
      if (!res.ok) throw new Error("No se pudo conectar con la API");
      const json = await res.json();
      setGraphData({
        nodes: json.nodes || [],
        links: json.links || [],
      });
    } catch (err: any) {
      console.error("Error fetching graph:", err);
      setError(err.message || "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filter by search
  const filteredNodeIds = useMemo(() => {
    if (!searchQuery) return new Set(graphData.nodes.map((n) => n.id));
    const q = searchQuery.toLowerCase();
    return new Set(
      graphData.nodes
        .filter(
          (n) =>
            n.label.toLowerCase().includes(q) ||
            n.nit.toLowerCase().includes(q)
        )
        .map((n) => n.id)
    );
  }, [graphData.nodes, searchQuery]);

  const filteredData = useMemo(() => {
    const nodes = graphData.nodes.filter((n) => filteredNodeIds.has(n.id));
    const nodeIds = new Set(nodes.map((n) => n.id));
    // Keep original indices for highlight logic
    const links = graphData.links
      .map((l, idx) => ({ ...l, _originalIdx: idx }))
      .filter(
        (l) => nodeIds.has(l.source) && nodeIds.has(l.target)
      );
    return { nodes, links };
  }, [graphData, filteredNodeIds]);

  // Build adjacency for highlight
  const adjacencyMap = useMemo(() => {
    const map = new Map<number, Set<number>>();
    graphData.links.forEach((link, idx) => {
      if (!map.has(link.source)) map.set(link.source, new Set());
      if (!map.has(link.target)) map.set(link.target, new Set());
      map.get(link.source)!.add(link.target);
      map.get(link.target)!.add(link.source);
    });
    return map;
  }, [graphData.links]);

  const handleNodeClick = useCallback(
    (node: Node) => {
      const connected = adjacencyMap.get(node.id) || new Set();
      connected.add(node.id);
      setHighlightNode(node.id);

      // Find link indices connected to this node
      const linkSet = new Set<number>();
      graphData.links.forEach((link, idx) => {
        if (link.source === node.id || link.target === node.id) {
          linkSet.add(idx);
        }
      });
      setHighlightLinks(linkSet);

      // Zoom to node
      if (fgRef.current) {
        fgRef.current.centerAt(node.x || 0, node.y || 0, 800);
        fgRef.current.zoom(2, 800);
      }
    },
    [adjacencyMap, graphData.links]
  );

  const handleBackgroundClick = useCallback(() => {
    setHighlightNode(null);
    setHighlightLinks(new Set());
  }, []);

  // Node color (Obsidian-style: mostly gray, with accents)
  const getNodeColor = (node: Node) => {
    if (highlightNode === null) {
      if (node.type === "entidad") return "#e0e0e0";
      if (node.sancionado) return "#ef4444";
      if (node.riesgo_max >= 70) return "#f97316";
      if (node.riesgo_max >= 55) return "#eab308";
      if (node.riesgo_max >= 40) return "#a3a3a3";
      return "#737373";
    }
    // When a node is highlighted
    const connected = adjacencyMap.get(highlightNode)?.has(node.id);
    if (node.id === highlightNode) return "#ffffff";
    if (connected) {
      if (node.type === "entidad") return "#e0e0e0";
      if (node.sancionado) return "#ef4444";
      if (node.riesgo_max >= 55) return "#f97316";
      return "#a3a3a3";
    }
    return "#2a2a2a"; // Dimmed
  };

  const getNodeRadius = (node: Node) => {
    if (node.type === "entidad") return 12;
    if (node.sancionado) return 7;
    if (node.riesgo_max >= 70) return 8;
    if (node.riesgo_max >= 55) return 7;
    return 4;
  };

  const getLinkColor = (link: Link & { _originalIdx?: number }) => {
    const idx = link._originalIdx ?? -1;
    if (highlightNode === null) return "#3a3a3a";
    return highlightLinks.has(idx) ? "#555555" : "#1a1a1a";
  };

  const getLinkWidth = (link: Link) => {
    return Math.min(link.num_contratos, 5);
  };

  const nodeOpacity = (node: Node) => {
    if (highlightNode === null) return 0.9;
    if (node.id === highlightNode) return 1;
    if (adjacencyMap.get(highlightNode)?.has(node.id)) return 0.85;
    return 0.15;
  };

  const linkOpacity = (link: Link & { _originalIdx?: number }) => {
    const idx = link._originalIdx ?? -1;
    if (highlightNode === null) return 0.4;
    return highlightLinks.has(idx) ? 0.7 : 0.05;
  };

  // Stats
  const stats = useMemo(() => {
    const entidades = graphData.nodes.filter((n) => n.type === "entidad");
    const proveedores = graphData.nodes.filter((n) => n.type === "proveedor");
    return {
      total: graphData.nodes.length,
      entidades: entidades.length,
      proveedores: proveedores.length,
      links: graphData.links.length,
    };
  }, [graphData]);

  // Selected node info
  const selectedNode = highlightNode !== null
    ? graphData.nodes.find((n) => n.id === highlightNode)
    : null;

  const formatCOP = (value: number) => {
    if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(0)}M`;
    return `$${value.toLocaleString()}`;
  };

  const riskLabel = (score: number) => {
    if (score >= 70) return "Crítico";
    if (score >= 55) return "Alto";
    if (score >= 40) return "Medio";
    return "Bajo";
  };

  if (loading) {
    return (
      <div className="h-screen bg-[#1a1a1a] flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-3 border-neutral-600 border-t-neutral-300 rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-neutral-500 text-sm">Construyendo el grafo...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen bg-[#1a1a1a] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-3">⚠ {error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-1.5 bg-neutral-800 text-neutral-300 text-sm rounded hover:bg-neutral-700 transition"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-[#1a1a1a] text-neutral-200 flex flex-col">
      {/* Top bar */}
      <div className="border-b border-neutral-800 px-4 py-2 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-semibold text-neutral-300">Graph</h1>
          <span className="text-xs text-neutral-600">
            {stats.entidades} entidades · {stats.proveedores} proveedores ·{" "}
            {stats.links} conexiones
          </span>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Buscar..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-3 py-1 bg-neutral-800 border border-neutral-700 rounded text-xs text-neutral-300 placeholder-neutral-600 focus:outline-none focus:border-neutral-500 w-48"
          />
          <button
            onClick={() => {
              setSearchQuery("");
              handleBackgroundClick();
            }}
            className="px-3 py-1 bg-neutral-800 text-neutral-500 text-xs rounded hover:bg-neutral-700 transition"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Main area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Graph */}
        <div ref={canvasRef} className="flex-1 relative">
          {filteredData.nodes.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-neutral-600 text-sm">
                No hay nodos que coincidan
              </p>
            </div>
          ) : (
            <ForceGraph2D
              ref={fgRef}
              graphData={filteredData}
              nodeColor={getNodeColor}
              nodeRelSize={1}
              nodeVal={getNodeRadius}
              nodeLabel={(node: Node) => {
                let label = node.label;
                if (node.sancionado) label += " ⛔";
                return label;
              }}
              linkColor={getLinkColor}
              linkWidth={getLinkWidth}
              linkDirectionalArrowLength={0}
              backgroundColor="#1a1a1a"
              cooldownTicks={120}
              warmupTicks={10}
              onNodeClick={handleNodeClick}
              onBackgroundClick={handleBackgroundClick}
              enableNodeDrag={true}
              // Labels always visible
              nodeCanvasObject={(node: Node, ctx: CanvasRenderingContext2D, globalScale: number) => {
                const label = node.label;
                const fontSize = Math.max(8, 11 / globalScale);
                const radius = getNodeRadius(node);

                // Node circle
                ctx.beginPath();
                ctx.arc(node.x!, node.y!, radius, 0, 2 * Math.PI, false);
                ctx.fillStyle = getNodeColor(node);
                ctx.globalAlpha = nodeOpacity(node);
                ctx.fill();

                // Label
                if (globalScale > 0.3 || node.type === "entidad" || node.id === highlightNode) {
                  ctx.font = `${node.type === "entidad" ? "bold " : ""}${fontSize}px Inter, sans-serif`;
                  ctx.fillStyle = getNodeColor(node) === "#2a2a2a" ? "#2a2a2a" : "#d4d4d4";
                  ctx.textAlign = "center";
                  ctx.textBaseline = "top";
                  ctx.globalAlpha = node.id === highlightNode ? 1 : (node.type === "entidad" ? 0.9 : 0.5);
                  const displayLabel = label.length > 25 ? label.substring(0, 25) + "…" : label;
                  ctx.fillText(displayLabel, node.x!, node.y! + radius + 4);
                }

                ctx.globalAlpha = 1;
              }}
              linkCanvasObject={(link: Link & { _originalIdx?: number }, ctx: CanvasRenderingContext2D, globalScale: number) => {
                ctx.strokeStyle = getLinkColor(link);
                ctx.globalAlpha = linkOpacity(link);
                ctx.lineWidth = Math.max(0.5, getLinkWidth(link) / globalScale);
                ctx.beginPath();
                ctx.moveTo(link.source.x || 0, link.source.y || 0);
                ctx.lineTo(link.target.x || 0, link.target.y || 0);
                ctx.stroke();
                ctx.globalAlpha = 1;
              }}
              linkCanvasObjectMode={() => "replace"}
              nodeCanvasObjectMode={() => "replace"}
            />
          )}
        </div>

        {/* Side panel — info del nodo seleccionado */}
        {selectedNode && (
          <div className="w-64 border-l border-neutral-800 bg-[#1e1e1e] p-4 shrink-0 overflow-y-auto">
            <button
              onClick={handleBackgroundClick}
              className="text-neutral-600 hover:text-neutral-300 text-xs mb-4"
            >
              ✕ Cerrar
            </button>

            <h2 className="text-sm font-semibold text-neutral-200 mb-1 break-words">
              {selectedNode.label}
            </h2>
            <p className="text-xs text-neutral-600 font-mono mb-3">
              {selectedNode.nit}
            </p>

            <div className="space-y-3">
              {/* Type badge */}
              <div className="flex items-center gap-2">
                <span
                  className={`w-2 h-2 rounded-full ${selectedNode.type === "entidad"
                    ? "bg-neutral-300"
                    : "bg-neutral-600"
                    }`}
                ></span>
                <span className="text-xs text-neutral-400">
                  {selectedNode.type === "entidad" ? "Entidad pública" : "Proveedor"}
                </span>
              </div>

              {/* Risk */}
              {selectedNode.type === "proveedor" && selectedNode.riesgo_max > 0 && (
                <div>
                  <p className="text-xs text-neutral-600 mb-1">Riesgo</p>
                  <p
                    className={`text-lg font-bold ${selectedNode.riesgo_max >= 70
                      ? "text-orange-500"
                      : selectedNode.riesgo_max >= 55
                        ? "text-yellow-500"
                        : "text-neutral-500"
                      }`}
                  >
                    {selectedNode.riesgo_max}/100
                  </p>
                  <p className="text-xs text-neutral-600">
                    {riskLabel(selectedNode.riesgo_max)}
                  </p>
                </div>
              )}

              {/* Sanctioned */}
              {selectedNode.sancionado && (
                <div className="bg-red-900/20 border border-red-900/50 rounded p-2">
                  <p className="text-red-400 text-xs font-semibold">
                    ⛔ Sancionado
                  </p>
                </div>
              )}

              {/* Connections count */}
              {highlightNode !== null && (
                <div>
                  <p className="text-xs text-neutral-600 mb-1">Conexiones</p>
                  <p className="text-sm text-neutral-300">
                    {adjacencyMap.get(selectedNode.id)?.size || 0} entidades/proveedores
                  </p>
                </div>
              )}

              {/* Contracts */}
              {selectedNode.contratos_alto_riesgo > 0 && (
                <div>
                  <p className="text-xs text-neutral-600 mb-1">
                    Contratos de alto riesgo
                  </p>
                  <p className="text-sm text-orange-400">
                    {selectedNode.contratos_alto_riesgo} de{" "}
                    {selectedNode.total_contratos_scored || "?"}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom legend */}
      <div className="border-t border-neutral-800 px-4 py-2 flex items-center gap-4 text-xs text-neutral-600 shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-neutral-300"></span>
          Entidad
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-neutral-600"></span>
          Proveedor
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
          Alto riesgo
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
          Crítico
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
          Sancionado
        </div>
        <span className="ml-auto text-neutral-700">
          Click en un nodo para resaltar · Click fuera para reset
        </span>
      </div>
    </div>
  );
}
