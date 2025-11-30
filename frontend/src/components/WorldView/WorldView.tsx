import React, { useEffect, useRef, useState } from "react";
import { type World } from "../../world";
import type { WorldStyle } from "../../App";
import "./WorldView.css";
import assetsMap from "../../assets/assetsMap.json";

const earthFiles = import.meta.glob("../../assets/themes/earth/*.png", {
  eager: true,
  as: "url",
});

const themeFiles: Record<WorldStyle, Record<string, string>> = {
  earth: earthFiles,
  mars: earthFiles,
  fantasy: earthFiles,
  scifi: earthFiles
};

function getAssetPathByWorldStyle(worldStyle: WorldStyle, propName: string, part: number): string | undefined {
  const fileName = (assetsMap as Record<string, string[]>)[propName][part];
  if (!fileName) return undefined;

  const files = themeFiles[worldStyle];
  const entry = Object.entries(files).find(([path]) => path.endsWith("/" + fileName));
  return entry?.[1]; // this is already the built URL string
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

  // Recalculate base tile size whenever world or container size changes
  useEffect(() => {
  if (!world) return;

  const updateBaseTileSize = () => {
    const el = containerRef.current;
    if (!el) return;

    const rect = el.getBoundingClientRect();
    const padding = 32; // keep if you like a frame, or set to 0 for full bleed
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

  if (loading) {
    return <div className="world-view generating-text">Generating world…</div>;
  }

  if (error) {
    return (
      <div className="world-view world-view-error">
        {error}
      </div>
    );
  }

  if (!world) {
    return (
      <div className="world-view world-view-placeholder">
        <span className="typing-text">Describe a world to begin...</span>
      </div>
    );
  }

  return (
  <div ref={containerRef} className={`world-view world-view--${styleVariant}`}>
    
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
        {world.tiles.map((tile, i) => (
          <div
            key={i}
            className={`world-tile world-tile--${tile.type}`}
            style={{
              left: tile.x * tileSize,
              top: tile.y * tileSize,
              width: tileSize,
              height: tileSize,
            }}
          />
        ))}

        {/* Objects */}
        {world.objects.map((obj) => (
  <div
    key={obj.id}
    className={`world-object world-object--${obj.kind}`}
    style={{
      backgroundImage: `url(${getAssetPathByWorldStyle(styleVariant, obj.kind, obj.part)})`,
      left: obj.x * tileSize,
      top: obj.y * tileSize,
      width: tileSize,
      height: tileSize,
    }}
    title={obj.name || obj.kind}

    // City label only on the center tile (part = 1)
    data-name={
      obj.kind === "city" && obj.part === 3 
        ? obj.name
        : undefined
    }

    // Give data-part to ANY object that has a part (city, tree, etc.)
    data-part={
      obj.part !== undefined
        ? String(obj.part)
        : undefined
    }
  />
))}
      </div>
    </div>

    {/* Zoom controls (outside scroll) */}
    <div className="world-view-zoom-controls">
      <button onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}>−</button>
      <span>{Math.round(zoom * 100)}%</span>
      <button onClick={() => setZoom((z) => Math.min(4, z + 0.25))}>+</button>
    </div>

  </div>
);
};
