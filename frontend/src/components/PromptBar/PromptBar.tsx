import { useState, type KeyboardEvent } from "react";
import "./PromptBar.css";

interface PromptBarProps {
  onSubmit: (prompt: string) => void;
}

export const PromptBar: React.FC<PromptBarProps> = ({ onSubmit }) => {
  const [value, setValue] = useState("");
  const [expanded, setExpanded] = useState(false);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setValue("");
    setExpanded(false); // optional: collapse after send
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter = send, Shift+Enter = new line
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`prompt-bar ${expanded ? "prompt-bar--expanded" : ""}`}>
      <textarea
        className="prompt-input"
        placeholder='Enter your world description... (Shift+Enter for new line)'
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <div className="prompt-actions">
        <button
          type="button"
          className="prompt-expand"
          onClick={() => setExpanded((prev) => !prev)}
        >
          {expanded ? "Collapse" : "Expand"}
        </button>
        <button className="prompt-send" onClick={handleSubmit}>
          Send
        </button>
      </div>
    </div>
  );
};
