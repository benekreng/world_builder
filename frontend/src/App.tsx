import { useState } from "react";
import { WorldView } from "./components/WorldView/WorldView";
import { StylePanel } from "./components/StylePanel/StylePanel";
import { PromptBar } from "./components/PromptBar/PromptBar";
import { type World } from "./world";
import { mapToWorld } from "./world.mapper";
import "./App.css";
import { Client } from "./api/client";

export type WorldStyle = "default";

function App() {
  const client = new Client("http://localhost:8000");
  const [worldStyle, setWorldStyle] = useState<WorldStyle>("default");
  const [lastPrompt, setLastPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [world, setWorld] = useState<World | null>(null);
  const [promptHistory, setPromptHistory] = useState<string[]>([]);

  setWorldStyle("default");

  const handlePromptSubmit = async (prompt: string) => {
    
    setLastPrompt(prompt);
    setPromptHistory((prev) => [prompt, ...prev]);

    setBusy(true);

    try {
      const taskId = await client.triggerWorldGeneration(prompt);
      const worldDto = await client.getGeneratedWorld(taskId);
      const world = mapToWorld(worldDto);
      setWorld(world);
    } catch (error) {
      // Ignore errors for now
    } finally {
      setBusy(false);
    }
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
