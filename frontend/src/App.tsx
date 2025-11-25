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

  // NEW: store prompt history for StylePanel
  const [promptHistory, setPromptHistory] = useState<string[]>([]);

  const handlePromptSubmit = async (prompt: string) => {
    // update last prompt + history
    setLastPrompt(prompt);
    setPromptHistory((prev) => [prompt, ...prev]); // newest first

    setBusy(true);
    // Simulate some work
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setWorld(mockWorld);
    setBusy(false);
  };

  // NEW: placeholder handlers for undo/redo
  const handleUndo = () => {
    // later: emit to backend
    console.log("Undo clicked");
  };

  const handleRedo = () => {
    // later: emit to backend
    console.log("Redo clicked");
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
          worldStyle={worldStyle}
          onChangeStyle={setWorldStyle}
          promptHistory={promptHistory}
          onUndo={handleUndo}
          onRedo={handleRedo}
        />
      </main>

      <footer className="app-footer">
        <PromptBar onSubmit={handlePromptSubmit} busy={busy} />
      </footer>
    </div>
  );
}

export default App;
