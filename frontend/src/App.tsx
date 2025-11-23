import { useState } from "react";
import { WorldView } from "./components/WorldView/WorldView";
import { StylePanel } from "./components/StylePanel/StylePanel";
import { PromptBar } from "./components/PromptBar/PromptBar";
import { mockWorld, type World } from "./components/WorldView/mockWorld";
import "./App.css";

export type WorldStyle = "mars" | "earth" | "fantasy" | "scifi";

function App() {
  const [worldStyle, setWorldStyle] = useState<WorldStyle>("mars");
  const [lastPrompt, setLastPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [world, setWorld] = useState<World | null>(null);

  const handlePromptSubmit = async (prompt: string) => {
    setLastPrompt(prompt);
    setBusy(true);
    // Simulate some work
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setWorld(mockWorld);
    setBusy(false);
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
        <WorldView styleVariant={worldStyle} lastPrompt={lastPrompt} loading={busy} error={null} world={world} />
        <StylePanel worldStyle={worldStyle} onChangeStyle={setWorldStyle} />
      </main>

      <footer className="app-footer">
        <PromptBar onSubmit={handlePromptSubmit} busy={busy} />
      </footer>
    </div>
  );
}

export default App;
