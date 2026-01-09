import React from "react";
import "./StylePanel.css";
import { PromptHistory } from "./PromptHistory/PromptHistory";

export interface StylePanelProps {
  promptHistory: string[];
}

export const StylePanel: React.FC<StylePanelProps> = ({
  promptHistory
}) => {
  return (
      <PromptHistory prompts={promptHistory} />
  );
};
