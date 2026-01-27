import { useState, useEffect } from "react";
import { WorldView } from "./components/WorldView/WorldView";
import { StylePanel } from "./components/StylePanel/StylePanel";
import { PromptBar } from "./components/PromptBar/PromptBar";
import { HistoryTree } from "./components/HistoryTree/HistoryTree";
import { type World } from "./world";
import { mapToWorld } from "./world.mapper";
import { generateMap, resetWorld, fetchHistory, fetchNodePrompts, jumpToNode, deleteNode, type HistoryNode } from "./api/client";
import "./App.css";

export type WorldStyle = "default";

function App() {
  const [worldStyle, setWorldStyle] = useState<WorldStyle>("default");
  const [lastPrompt, setLastPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [world, setWorld] = useState<World | null>(null);

  const [historyNodes, setHistoryNodes] = useState<HistoryNode[]>([]);
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  
  const [displayedPromptHistory, setDisplayedPromptHistory] = useState<string[]>([]);

  const refreshHistory = async () => {
    try {
      const data = await fetchHistory();
      setHistoryNodes(data.nodes);
      setActiveNodeId(data.current_node_id);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (world) {
      refreshHistory();
    } else {
      //If world is null, ensure all history state is wiped visually
      setHistoryNodes([]);
      setActiveNodeId(null);
      setSelectedNodeId(null);
      setDisplayedPromptHistory([]);
    }
  }, [world]);

  useEffect(() => {
    const targetId = selectedNodeId || activeNodeId;
    if (targetId) {
      fetchNodePrompts(targetId).then((prompts) => {
        setDisplayedPromptHistory(prompts);
      });
    } else {
      setDisplayedPromptHistory([]);
    }
  }, [selectedNodeId, activeNodeId]);


  const handleReset = async () => {
    //Only ask for confirmation if there is actually a world to delete
    if (world && !window.confirm("Are you sure you want to reset the world? All history will be lost.")) {
      return;
    }

    setBusy(true);
    try {
      await resetWorld();
      //Full State Wipe
      setWorld(null);
      setLastPrompt("");
      setHistoryNodes([]);
      setActiveNodeId(null);
      setSelectedNodeId(null);
      setDisplayedPromptHistory([]);
    } catch (error) {
      console.error("Failed to reset:", error);
    } finally {
      setBusy(false);
    }
  };

  const handlePromptSubmit = async (prompt: string) => {
    setWorldStyle("default");
    setLastPrompt(prompt);
    setBusy(true);
    if (!world) {
      setWorld(null); 
    }

    try {
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

  const handleJump = async (id: string) => {
    setBusy(true);
    try {
      const response = await jumpToNode(id);        
      const worldData = response.result ? response.result : response;        
      console.log("Jump received data:", worldData);

      if (worldData && worldData.entities) {
          setWorld(mapToWorld(worldData));
      } else {
          console.error("Received invalid world data:", worldData);
      }
      setSelectedNodeId(null);
      await refreshHistory();
    } catch(e) { 
      console.error("Jump failed:", e); 
    } finally { 
      setBusy(false); 
    }
  }

  const handleDeleteHistory = async (id: string) => {
    setBusy(true);
    try {
        await deleteNode(id);
        if (id === activeNodeId) {
            const check = await fetchHistory();
            if (!check.current_node_id) {
                setWorld(null);
            } else {
                await handleJump(check.current_node_id);
            }
        } else {
            await refreshHistory();
        }
        setSelectedNodeId(null);
    } catch(e) { 
      console.error(e); 
    } finally { 
      setBusy(false); 
    }
  }

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

          <div style={{ display: 'flex', gap: '10px' }}>
            {/*Reset button*/}
            <button 
              onClick={handleReset} 
              disabled={busy} 
              style={{
                padding: "8px 16px", background: "#c25e5e", color: "white", 
                border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold"
              }}
            >
              Reset World
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        
        {/*1. Map*/}
        <div className="map-container">
          <WorldView
            styleVariant={worldStyle}
            lastPrompt={lastPrompt}
            loading={busy}
            error={null}
            world={world}
          />
        </div>

        {/*2. Timeline*/}
        <div className="history-column">
          <HistoryTree 
              nodes={historyNodes}
              activeNodeId={activeNodeId}
              selectedNodeId={selectedNodeId}
              onSelect={setSelectedNodeId}
              onJump={handleJump}
              onDelete={handleDeleteHistory}
              busy={busy}
          />
        </div>

        {/*3. Tools/Log*/}
        <div className="tools-column">
          <StylePanel promptHistory={displayedPromptHistory} /> 
        </div>

      </main>

      <footer className="app-footer">
        <PromptBar onSubmit={handlePromptSubmit} busy={busy} />
      </footer>
    </div>
  );
}

export default App;