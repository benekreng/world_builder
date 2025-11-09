import { useState } from "react";
import { WorldView } from "./components/WorldView/WorldView";
import { StylePanel } from "./components/StylePanel/StylePanel";
import { PromptBar } from "./components/PromptBar/PromptBar";
import "./App.css";

export type WorldStyle = "mars" | "earth" | "fantasy" | "scifi";

function App() {
  const [worldStyle, setWorldStyle] = useState<WorldStyle>("mars");
  const [lastPrompt, setLastPrompt] = useState("");

  const handlePromptSubmit = (prompt: string) => {
    setLastPrompt(prompt);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1 className="app-title">World Builder</h1>
          <p className="app-subtitle">
            Describe a world. We’ll generate the structure. Styles are visual only.
          </p>
        </div>
      </header>

      <main className="app-main">
        <WorldView styleVariant={worldStyle} lastPrompt={lastPrompt} />
        <StylePanel worldStyle={worldStyle} onChangeStyle={setWorldStyle} />
      </main>

      <footer className="app-footer">
        <PromptBar onSubmit={handlePromptSubmit} />
      </footer>
    </div>
  );
}

export default App;
