import { useState } from "react";
import { WorldView } from "./components/WorldView/WorldView";
import { StylePanel } from "./components/StylePanel/StylePanel";
import { PromptBar } from "./components/PromptBar/PromptBar";
import { type World } from "./world";
import { mapToWorld } from "./world.mapper";
import { generateMap, resetWorld, undoWorld, redoWorld } from "./api/client";
import "./App.css";

export type WorldStyle = "default";

function App() {
  const [worldStyle, setWorldStyle] = useState<WorldStyle>("default");
  const [lastPrompt, setLastPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [world, setWorld] = useState<World | null>(null);

  const [promptHistory, setPromptHistory] = useState<string[]>([]);

  //Handler for resetting the world
  const handleReset = async () => {
    if (!world) return;
    if (!window.confirm("Start a new world? This will delete the current map.")) return;

    setBusy(true);
    try {
      await resetWorld();
      setWorld(null);
      setLastPrompt("");
      setPromptHistory([]);
    } catch (error) {
      console.error("Failed to reset:", error);
    } finally {
      setBusy(false);
    }
  };

  const handleUndo = async () => {
    if (busy || !world) return;
    setBusy(true);
    try {
      const rawData = await undoWorld();
      setWorld(mapToWorld(rawData));
    } catch (error) {
      console.warn("Undo unavailable:", error);
    } finally {
      setBusy(false);
    }
  };

  const handleRedo = async () => {
    if (busy || !world) return;
    setBusy(true);
    try {
      const rawData = await redoWorld();
      setWorld(mapToWorld(rawData));
    } catch (error) {
      console.warn("Redo unavailable:", error);
    } finally {
      setBusy(false);
    }
  };

  const handlePromptSubmit = async (prompt: string) => {
    setWorldStyle("default");
    setLastPrompt(prompt);
    setPromptHistory((prev) => [prompt, ...prev]);
    
    setBusy(true);
    
    if (!world) {
      setWorld(null); 
    }

    try {
      //The backend now returns a WorldDto directly
      const rawData = await generateMap(prompt) as any; 
      const mappedWorld = mapToWorld(rawData);
      setWorld(mappedWorld);
    } catch (error) {
      console.error("Failed to generate map:", error);
      alert("Error generating map. Check console for details.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="app-title">World Builder</h1>
            <p className="app-subtitle">
              {world ? "Describe a change..." : "Describe a world. We’ll generate the map."}
            </p>
          </div>

          {/* CONTROLS */}
          <div style={{ display: 'flex', gap: '10px' }}>
            {world && (
              <>
                <button 
                  onClick={handleUndo} 
                  disabled={busy}
                  className="secondary-btn" // Add CSS for this if needed, or inline style
                  style={{ padding: "8px 12px", cursor: "pointer" }}
                >
                  ↩ Undo
                </button>
                <button 
                  onClick={handleRedo} 
                  disabled={busy}
                  className="secondary-btn"
                  style={{ padding: "8px 12px", cursor: "pointer" }}
                >
                  ↪ Redo
                </button>
                
                <button 
                  onClick={handleReset} 
                  disabled={busy}
                  style={{
                    padding: "8px 16px",
                    background: "#c25e5e",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: busy ? "wait" : "pointer",
                    fontWeight: "bold"
                  }}
                >
                  New World
                </button>
              </>
            )}
          </div>
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