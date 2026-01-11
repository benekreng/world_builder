import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from world_builder.app import WorldBuilder

app = FastAPI(title="API for World Builder")

core = WorldBuilder()

# In-Memory Speicher für Tasks 
# Struktur: {"task_id": {"status": "processing", "result": None}}
tasks: Dict[str, Dict[str, Any]] = {}

origins = ["http://localhost", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

# Hilfsfunktion für den Hintergrund-Prozess
async def run_map_pipeline(task_id: str, prompt: str):
    try:
        final_graph = await core.map_pipeline.run(prompt)
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = final_graph.model_dump()
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = {"error": str(e)}

@app.post("/generate-map", response_model=Dict[str, str])
async def generate_map(request: GenerateRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # Task initialisieren
    tasks[task_id] = {"status": "processing", "result": None}
    
    background_tasks.add_task(run_map_pipeline, task_id, request.prompt)
    
    # ID zurückgeben, Frontend ist nicht blockiert
    return {"task_id": task_id}

@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")
    
    return {
        "task_id": task_id,
        "status": tasks[task_id]["status"],
        "result": tasks[task_id]["result"]
    }

@app.get("/")
async def root():
    return {"message": "Server is running"}
