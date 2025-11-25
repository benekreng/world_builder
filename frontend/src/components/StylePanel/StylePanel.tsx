import React from "react";
import type { WorldStyle } from "../../App";
import "./StylePanel.css";
import { UndoRedoBar } from "./UndoRedoBar/UndoRedoBar";
import { MapStyleDropdown } from "./MapStyleDropdown/MapStyleDropdown";
import { PromptHistory } from "./PromptHistory/PromptHistory";


export interface StylePanelProps {
  worldStyle: WorldStyle;
  onChangeStyle: (style: WorldStyle) => void;
  promptHistory: string[];
  onUndo: () => void;
  onRedo: () => void;
}

export const StylePanel: React.FC<StylePanelProps> = ({
  worldStyle,
  onChangeStyle,
  promptHistory,
  onUndo,
  onRedo,
}) => {
  return (
    <aside className="style-panel">
      <div className="style-panel-header">
        <h2 className="style-panel-title">Map Configurator</h2>
        <UndoRedoBar onUndo={onUndo} onRedo={onRedo} />
      </div>

      <p className="style-panel-subtitle">
        Choose a visual theme. The generated structure stays the same.
      </p>

      <MapStyleDropdown value={worldStyle} onChange={onChangeStyle} />

      <PromptHistory prompts={promptHistory} />
    </aside>
  );
};
