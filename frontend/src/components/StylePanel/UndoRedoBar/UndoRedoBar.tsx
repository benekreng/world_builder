import React from "react";
import "../StylePanel.css";


interface UndoRedoBarProps {
  onUndo: () => void;
  onRedo: () => void;
}

export const UndoRedoBar: React.FC<UndoRedoBarProps> = ({
  onUndo,
  onRedo,
}) => {
  return (
    <div className="style-panel-history-buttons">
      <button
        type="button"
        className="style-history-btn"
        onClick={onUndo}
      >
        Undo
      </button>
      <button
        type="button"
        className="style-history-btn"
        onClick={onRedo}
      >
        Redo
      </button>
    </div>
  );
};
