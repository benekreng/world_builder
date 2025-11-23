import React, { useEffect, useRef, useState } from "react";
import { type World } from "./mockWorld";
import type { WorldStyle } from "../../App";
import "./WorldView.css";

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
  error}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [tileSize, setTileSize] = useState(24);

  // Recalculate tile size whenever world or container size changes
  useEffect(() => {
    if (!world) return;

    const updateTileSize = () => {
      const el = containerRef.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();

      // leave a little padding inside
      const padding = 32;
      const availableWidth = Math.max(rect.width - padding, 50);
      const availableHeight = Math.max(rect.height - padding, 50);

      const size = Math.floor(
        Math.min(
          availableWidth / world.width,
          availableHeight / world.height
        )
      );

      // clamp so it never becomes 0
      setTileSize(size > 4 ? size : 4);
    };

    updateTileSize();
    window.addEventListener("resize", updateTileSize);
    return () => window.removeEventListener("resize", updateTileSize);
  }, [world]);

  if (loading) {
    return <div className="world-view">Generating world…</div>;
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
        Describe a world to begin.
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`world-view world-view--${styleVariant}`}
    >
      <div
        className="world-grid"
        style={{
          width: world.width * tileSize,
          height: world.height * tileSize,
        }}
      >
        {world.tiles.map((tile, i) => (
          <div
            key={i}
            className={`world-tile world-tile--${tile.type}`}
            style={{
              left: tile.x * tileSize,
              top: tile.y * tileSize,
            }}
          />
        ))}

        {world.objects.map((obj) => (
  <div
    key={obj.id}
    className={`world-object world-object--${obj.kind}`}
    style={{
      left: obj.x * tileSize,
      top: obj.y * tileSize,
    }}
    title={obj.name || obj.kind}
    data-name={obj.kind === "city" ? obj.name : undefined}
  />
))}
      </div>
    </div>
  );
};
