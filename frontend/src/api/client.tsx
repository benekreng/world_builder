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

export const undoWorld = async (): Promise<WorldDto> => {
  const url = `${API_BASE_URL}/undo`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    throw new Error("Undo not available"); 
  }
  const data = await response.json();
  return data.result as WorldDto; 
};

export const redoWorld = async (): Promise<WorldDto> => {
  const url = `${API_BASE_URL}/redo`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    throw new Error("Redo not available"); 
  }
  const data = await response.json();
  return data.result as WorldDto;
};