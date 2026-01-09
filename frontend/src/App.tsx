import { useState } from "react";
import { WorldView } from "./components/WorldView/WorldView";
import { StylePanel } from "./components/StylePanel/StylePanel";
import { PromptBar } from "./components/PromptBar/PromptBar";
import { mockWorld, type World } from "./world";
import "./App.css";

export type WorldStyle = "default";

function App() {
  const [worldStyle, setWorldStyle] = useState<WorldStyle>("default");
  const [lastPrompt, setLastPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [world, setWorld] = useState<World | null>(null);

  // NEW: store prompt history for StylePanel
  const [promptHistory, setPromptHistory] = useState<string[]>([]);

  const handlePromptSubmit = async (prompt: string) => {
    // update last prompt + history
    setWorldStyle("default");
    setLastPrompt(prompt);
    setPromptHistory((prev) => [prompt, ...prev]); // newest first

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
            Describe a world. We’ll generate the map.
          </p>
        </div>
      </header>

      <main className="app-main">
        <WorldView
          styleVariant={worldStyle}
          lastPrompt={lastPrompt}
          loading={busy}
          error={null}
          world={world}
        />

        <StylePanel
          promptHistory={promptHistory}
        />
      </main>

      <footer className="app-footer">
        <PromptBar onSubmit={handlePromptSubmit} busy={busy} />
      </footer>
    </div>
  );
}

export default App;
