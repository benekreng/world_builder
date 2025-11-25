import React from "react";
import "../StylePanel.css";

interface PromptHistoryProps {
  prompts: string[];
}

export const PromptHistory: React.FC<PromptHistoryProps> = ({ prompts }) => {
  const [expanded, setExpanded] = React.useState<Record<number, boolean>>({});

  const toggleExpanded = (idx: number) => {
    setExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  if (!prompts.length) {
    return (
      <div className="prompt-history prompt-history--empty">
        No prompts yet.
      </div>
    );
  }

  const total = prompts.length;

  return (
    <div className="prompt-history">
      <h3 className="prompt-history-title">Prompt History</h3>
      <ul className="prompt-history-list">
        {prompts.map((prompt, idx) => {
          const words = prompt.trim().split(/\s+/).filter(Boolean);
          const isLong = words.length > 50;
          const isExpanded = !!expanded[idx];

          const displayText =
            isLong && !isExpanded
              ? words.slice(0, 50).join(" ") + "…"
              : prompt;

          // newest prompt (idx 0) gets highest number
          const number = total - idx;

          return (
            <li key={idx} className="prompt-history-item">
              <div className="prompt-history-index">{number}.</div>
              <div className="prompt-history-bubble">
                <div className="prompt-history-text">{displayText}</div>
                {isLong && (
                  <button
                    type="button"
                    className="prompt-history-toggle"
                    onClick={() => toggleExpanded(idx)}
                  >
                    {isExpanded ? "Show less" : "Show more"}
                  </button>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
