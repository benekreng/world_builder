import React, { useMemo, useState, useRef, useEffect } from "react";
import type { HistoryNode } from "../../api/client";
import "./HistoryTree.css";

interface HistoryTreeProps {
  nodes: HistoryNode[];
  activeNodeId: string | null;
  selectedNodeId: string | null;
  onSelect: (id: string | null) => void;
  onJump: (id: string) => void;
  onDelete: (id: string) => void;
  busy: boolean;
}

interface LayoutNode extends HistoryNode {
  x: number;
  y: number;
  width: number;
  children: LayoutNode[];
}

const NODE_RADIUS = 14;
const VERTICAL_SPACING = 60;
const HORIZONTAL_SPACING = 50;

export const HistoryTree: React.FC<HistoryTreeProps> = ({ 
  nodes, activeNodeId, selectedNodeId, onSelect, onJump, onDelete, busy 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  const { layoutNodes, svgWidth, svgHeight } = useMemo(() => {
    if (nodes.length === 0) return { layoutNodes: [], svgWidth: 0, svgHeight: 0 };

    //A. Build Hierarchy Map
    const nodeMap = new Map<string, LayoutNode>();
    
    //Initialize map
    nodes.forEach(n => {
      nodeMap.set(n.id, { ...n, x: 0, y: 0, width: 0, children: [] });
    });

    //Link parents/children
    nodes.forEach(n => {
      const current = nodeMap.get(n.id)!;
      if (n.parent_id && nodeMap.has(n.parent_id)) {
        const parent = nodeMap.get(n.parent_id)!;
        parent.children.push(current);
      }
    });

    const root = Array.from(nodeMap.values()).find(n => !n.parent_id || !nodeMap.has(n.parent_id));

    if (!root) return { layoutNodes: [], svgWidth: 0, svgHeight: 0 };

    //Sort children by time
    nodeMap.forEach(n => {
        n.children.sort((a, b) => nodes.indexOf(a) - nodes.indexOf(b));
    });

    //B. Recursive Layout Calculation
    const calculateWidths = (node: LayoutNode) => {
        if (node.children.length === 0) {
            node.width = HORIZONTAL_SPACING;
            return;
        }
        let sumWidth = 0;
        node.children.forEach(child => {
            calculateWidths(child);
            sumWidth += child.width;
        });
        node.width = Math.max(HORIZONTAL_SPACING, sumWidth);
    };

    let maxX = 0;
    let maxY = 0;
    
    const assignCoords = (node: LayoutNode, xCenter: number, depth: number) => {
        node.x = xCenter;
        node.y = depth * VERTICAL_SPACING + 40;

        maxX = Math.max(maxX, node.x);
        maxY = Math.max(maxY, node.y);

        let currentX = xCenter - (node.width / 2);
        
        node.children.forEach(child => {
            const childX = currentX + (child.width / 2);
            assignCoords(child, childX, depth + 1);
            currentX += child.width;
        });
    };

    calculateWidths(root);
    assignCoords(root, root.width / 2 + 20, 0);

    return { 
        layoutNodes: Array.from(nodeMap.values()), 
        svgWidth: Math.max(maxX + 100, 300), 
        svgHeight: maxY + 100 
    };

  }, [nodes]);

  useEffect(() => {
    if(activeNodeId && containerRef.current) {
        const n = layoutNodes.find(n => n.id === activeNodeId);
        if(n) {
            containerRef.current.scrollTo({
                top: n.y - 150,
                left: n.x - containerRef.current.clientWidth / 2,
                behavior: 'smooth'
            });
        }
    }
  }, [activeNodeId, layoutNodes.length]);


  const getParent = (id: string | null) => layoutNodes.find(n => n.id === id);
  const selectedLayoutNode = layoutNodes.find(n => n.id === selectedNodeId);

  return (
    <div className="history-tree-container">
      <div className="history-header-area">
        <h3 className="history-title">Timeline</h3>
        <p className="history-subtitle">
            {nodes.length} States • {layoutNodes.filter(n => n.children.length > 1).length} Branches
        </p>
      </div>

      <div className="tree-viewport" ref={containerRef}>
        <svg width={svgWidth} height={svgHeight}>
            {/*1. Edges*/}
            {layoutNodes.map(node => {
                if (!node.parent_id) return null;
                const parent = getParent(node.parent_id);
                if (!parent) return null;

                //Curve
                const pathD = `M ${parent.x} ${parent.y + NODE_RADIUS} 
                               C ${parent.x} ${parent.y + VERTICAL_SPACING/2},
                                 ${node.x} ${node.y - VERTICAL_SPACING/2},
                                 ${node.x} ${node.y - NODE_RADIUS}`;

                return (
                    <path 
                        key={`edge-${node.id}`} 
                        d={pathD} 
                        className="tree-edge"
                    />
                );
            })}

            {/*2. Nodes*/}
            {layoutNodes.map(node => {
                const isSelected = node.id === selectedNodeId;
                const isActive = node.id === activeNodeId;
                
                return (
                    <g 
                        key={node.id} 
                        className="tree-node-group"
                        onClick={(e) => { e.stopPropagation(); onSelect(isSelected ? null : node.id); }}
                    >
                        {/*Type Color*/}
                        <circle 
                            cx={node.x} cy={node.y} r={NODE_RADIUS} 
                            className={`node-circle fill-${node.type} ${isSelected ? 'selected' : ''}`}
                        />
                        
                        {/*Inner Dot (Active State)*/}
                        {isActive && (
                            <circle cx={node.x} cy={node.y} r={5} className="node-dot" />
                        )}

                        {/*Hover Tooltip*/}
                        <title>{node.prompt}</title>
                    </g>
                );
            })}
        </svg>

        {/*3. Popup overlay (HTML over SVG) */}
        {selectedLayoutNode && (
            <div 
                className="history-popup"
                style={{
                    left: Math.min(selectedLayoutNode.x + 20, svgWidth - 230), 
                    top: selectedLayoutNode.y - 10
                }}
                onClick={(e) => e.stopPropagation()}
            >
                <div className="popup-header">
                    <span className="popup-title">Details</span>
                    <button className="popup-close-x" onClick={() => onSelect(null)}>×</button>
                </div>
                <div className="popup-body">
                    <p className="popup-prompt">"{selectedLayoutNode.prompt}"</p>
                    <div style={{fontSize: '0.75rem', color: '#666', marginBottom: '8px'}}>
                        Type: <strong>{selectedLayoutNode.type}</strong>
                    </div>
                </div>
                <div className="popup-actions">
                    {activeNodeId !== selectedLayoutNode.id && (
                        <button className="action-btn jump-btn" onClick={() => onJump(selectedLayoutNode.id)} disabled={busy}>
                            Move Here
                        </button>
                    )}
                    <button className="action-btn delete-btn" onClick={() => {
                        if(window.confirm("Delete this branch?")) onDelete(selectedLayoutNode.id);
                    }} disabled={busy}>
                        Delete
                    </button>
                </div>
            </div>
        )}
      </div>
    </div>
  );
};