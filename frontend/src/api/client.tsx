import { type WorldDto } from "../world.dto";

const API_BASE_URL = "http://localhost:8000"; 

export const generateMap = async (prompt: string): Promise<WorldDto> => {
  const url = `${API_BASE_URL}/generate-map`;

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Server Error: ${response.status} - ${errorText}`);
  }

  const { task_id } = await response.json();
  console.log(`Task started: ${task_id}`);

  const pollUrl = `${API_BASE_URL}/tasks/${task_id}`;
  
  while (true) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const statusRes = await fetch(pollUrl);
    if (!statusRes.ok) throw new Error("Polling failed");
    
    const data = await statusRes.json();
    
    if (data.status === "completed") {
      return data.result as WorldDto; 
    } else if (data.status === "failed") {
      throw new Error(data.result?.error || "Unknown error");
    }
  }
};

export const resetWorld = async (): Promise<void> => {
  const url = `${API_BASE_URL}/reset`;
  const response = await fetch(url, {
    method: "POST",
  });
  if (!response.ok) {
    console.error("Failed to reset world backend");
  }
};

//History
export interface HistoryNode {
  id: string;
  parent_id: string | null;
  prompt: string;
  type: "genesis" | "add" | "edit" | "remove" | "mixed";
  is_current: boolean;
}

export interface HistoryResponse {
  nodes: HistoryNode[];
  current_node_id: string | null;
}

export async function fetchHistory(): Promise<HistoryResponse> {
  const res = await fetch(`${API_BASE_URL}/history`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}

export async function fetchNodePrompts(nodeId: string): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/history/${nodeId}/prompts`);
  if (!res.ok) return [];
  return res.json();
}

export async function jumpToNode(nodeId: string) {
  const res = await fetch(`${API_BASE_URL}/history/jump/${nodeId}`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to jump history");
  const data = await res.json();
  return data.result; 
}

export async function deleteNode(nodeId: string) {
  const res = await fetch(`${API_BASE_URL}/history/${nodeId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete history node");
  return res.json();
}