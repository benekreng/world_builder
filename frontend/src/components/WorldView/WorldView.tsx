import React from "react";
import type { WorldStyle } from "../../App";
import "./WorldView.css";

interface WorldViewProps {
  styleVariant: WorldStyle;
  lastPrompt: string;
}

export const WorldView: React.FC<WorldViewProps> = ({
  styleVariant,
  lastPrompt,
}) => {
  return (
    <div className={`world-view world-view--${styleVariant}`}>
      <h2 className="world-view-title">World Visualization</h2>
      <div className="world-view-placeholder">
        {lastPrompt
          ? <>Last prompt: <strong>{lastPrompt}</strong></>
          : "Your world will render here"}
      </div>
    </div>
  );
};
