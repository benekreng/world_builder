import React, { useEffect, useRef, useState, useMemo } from "react";
import { type World } from "../../world";
import type { WorldStyle } from "../../App";
import "./WorldView.css";
import assetsMap from "../../assets/assetsMap.json";

const defaultFiles = import.meta.glob("../../assets/themes/default/*.png", {
  eager: true,
  as: "url",
});

const themeFiles: Record<WorldStyle, Record<string, string>> = {
  default: defaultFiles
};

function getAssetPathByWorldStyle(worldStyle: WorldStyle, propName: string, part: number): string | undefined {
  const fileName = (assetsMap as Record<string, string[]>)[propName]?.[part];
  if (!fileName) return undefined;

  const files = themeFiles[worldStyle];
  const entry = Object.entries(files).find(([path]) => path.endsWith("/" + fileName));
  return entry?.[1];
}

interface WorldViewProps {
  styleVariant: WorldStyle;
  world: World | null;
  loading: boolean;
  error: string | null;
  lastPrompt: string | null;
}

export const WorldView: React.FC<WorldViewProps> = ({
  styleVariant,
  world,
  loading,
  error,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [baseTileSize, setBaseTileSize] = useState(24); 
  const [zoom, setZoom] = useState(1);                  
  const tileSize = Math.max(Math.floor(baseTileSize * zoom), 4);
  
  const [hoverInfo, setHoverInfo] = useState<{ x: number, y: number, label: string } | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  
  //For label next to cursor
  const handleMouseMove = (e: React.MouseEvent) => {
    //Check if we are hovering a tile or object with data attributes
    const target = e.target as HTMLElement;
    
    //Prioritize Object's name/kind, then fall back to Tile's name/kind
    const name = target.dataset.name;
    const kind = target.dataset.kind;
    
    let label = null;
    if (name) label = name;
    //Don't label ground
    else if (kind && kind !== "ground") label = kind;
    
    if (label) {
      setHoverInfo({ x: e.clientX, y: e.clientY, label });
    } else {
      setHoverInfo(null);
    }
  };
  const handleMouseLeave = () => setHoverInfo(null);

  const handleEntityClick = (e: React.MouseEvent, id: string | null) => {
    e.stopPropagation();
    if (id) setSelectedId(id);
  };

  const closePopup = () => setSelectedId(null);

  const selectedCells = useMemo(() => {
    if (!world || !selectedId) return [];

    const cells: { x: number; y: number }[] = [];
    
    // 1. Check Objects
    world.objects.forEach((obj) => {
      if (obj.id === selectedId) cells.push({ x: obj.x, y: obj.y });
    });
    
    // 2. Check Tiles (Ground/Water)
    world.tiles.forEach((tile) => {
      if (tile.entityId === selectedId) cells.push({ x: tile.x, y: tile.y });
    });

    return cells;
  }, [world, selectedId]);


  useEffect(() => {
    if (!world) return;

    const updateBaseTileSize = () => {
      const el = containerRef.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const padding = 32; 
      const availableWidth = Math.max(rect.width - padding, 50);
      const availableHeight = Math.max(rect.height - padding, 50);

      const fitWidth = availableWidth / world.width;
      const fitHeight = availableHeight / world.height;

      // ⬅️ fill the container instead of fitting inside
      const size = Math.max(fitWidth, fitHeight);

      setBaseTileSize(size > 4 ? size : 4);
    };

    updateBaseTileSize();
    window.addEventListener("resize", updateBaseTileSize);
    return () => window.removeEventListener("resize", updateBaseTileSize);
  }, [world]);

  if (error) {
    return <div className="world-view world-view-error">{error}</div>;
  }

  //If we have no world yet:
  if (!world) {
    //If loading and no world -> Initial Generation
    if (loading) return <div className="world-view generating-text">Generating First World...</div>;
    //Else -> Placeholder
    return <div className="world-view world-view-placeholder"><span className="typing-text">Describe a world to begin...</span></div>;
  }

  const selectedMeta = selectedId ? world.meta[selectedId] : null;

  return (
    <div ref={containerRef} 
        className={`world-view world-view--${styleVariant}`} 
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onClick={closePopup}>
      
      {/*Loading Overlay*/}
      {loading && (
         <div className="loading-overlay">
           <div className="spinner"></div>
           <span>Updating World...</span>
         </div>
      )}
      
      {/* Scroll container */}
      <div className="world-scroll">
        <div
          className="world-grid"
          style={{
            width: world.width * tileSize,
            height: world.height * tileSize,
          }}
        >
          {/* Tiles */}
          {world.tiles.map((tile, i) => {
            const meta = tile.entityId ? world.meta[tile.entityId] : null;
            const name = meta?.name;

            return (
              <div
                key={i}
                className={`world-tile world-tile--${tile.type}`}
                style={{
                  backgroundImage: `url(${getAssetPathByWorldStyle(styleVariant, tile.type, 0)})`,
                  left: tile.x * tileSize,
                  top: tile.y * tileSize,
                  width: tileSize,
                  height: tileSize,
                }}
                //Data for Hover Label
                data-name={name}
                data-kind={tile.type}
                onClick={(e) => handleEntityClick(e, tile.entityId)}
              />
            );
          })}

          {/* Objects */}
          {world.objects.map((obj: any) => {

            //Unique key Creation
            const uniqueKey = `${obj.id}-${obj.x}-${obj.y}`

            return (
              <div
                key={uniqueKey}
                className={`world-object world-object--${obj.kind}`}
                style={{
                  backgroundImage: `url(${getAssetPathByWorldStyle(styleVariant, obj.kind, obj.part)})`,
                  left: obj.x * tileSize,
                  top: obj.y * tileSize,
                  width: tileSize,
                  height: tileSize,
                }}
                //Data for Hover Label
                data-name={obj.name}
                data-kind={obj.kind}
                onClick={(e) => handleEntityClick(e, obj.id)}
              />
            );
          })}
          
          {/*Selection Outline Layer */}
          {selectedCells.length > 0 && (
            <div className="selection-layer">
              {selectedCells.map((cell, i) => (
                <div
                  key={i}
                  className="selection-cell"
                  style={{
                    left: cell.x * tileSize,
                    top: cell.y * tileSize,
                    width: tileSize,
                    height: tileSize,
                  }}
                />
              ))}
              </div>
          )}
        </div>
      </div>
      
      {/*Cursor Tooltip */}
      {hoverInfo && (
        <div
          className="cursor-tooltip"
          style={{ left: hoverInfo.x + 15, top: hoverInfo.y + 15 }}
        >
          {hoverInfo.label}
        </div>
      )}

      {/*Info Popup */}
      {selectedId && selectedMeta && (
        <div className="info-popup" onClick={(e) => e.stopPropagation()}>
          <button className="close-btn" onClick={closePopup}>×</button>
          <h2>{selectedMeta.name || "Unknown Entity"}</h2>
          <div className="info-content">
            {selectedMeta.description && <p>{selectedMeta.description}</p>}
            {/* Render other metadata props */}
            {Object.entries(selectedMeta).map(([k, v]) => {
              if (k === 'name' || k === 'description' || k === 'color') return null;
              return <div key={k}><strong>{k}:</strong> {String(v)}</div>;
            })}
          </div>
        </div>
      )}

      {/* Zoom controls (outside scroll) */}
      <div className="world-view-zoom-controls">
        <button onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}>−</button>
        <span>{Math.round(zoom * 100)}%</span>
        <button onClick={() => setZoom((z) => Math.min(4, z + 0.25))}>+</button>
      </div>

    </div>
  );
};