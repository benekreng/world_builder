import uuid
import traceback
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from world_builder.app import WorldBuilder
from world_builder.rasterizer import MapRasterizer

app = FastAPI(title="API for World Builder")

core = WorldBuilder()

tasks: Dict[str, Dict[str, Any]] = {}

origins = ["http://localhost", "http://localhost:3000", "http://localhost:5173"]
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

async def run_world_generation_task(task_id: str, prompt: str):
    try:
        #Check if we already have a world in memory
        current_state = core.get_current_state()
        
        if current_state is None:
            #Genesis: Generate New World
            print(f"[{task_id}] No existing world. Running GENESIS with prompt: '{prompt}'")
            await core.create_world(prompt)
        else:
            #Evolution: Update existing world
            print(f"[{task_id}] World exists. Running EVOLUTION with instruction: '{prompt}'")
            await core.update_world(prompt)
            
        #Get the NEW state (result of create or update)
        new_state = core.get_current_state()
        if not new_state:
            raise Exception("World generation returned no state.")

        #Rasterize the graph stored in the State
        print(f"[{task_id}] Rasterizing graph with {len(new_state.graph.features)} features...")
        
        #settings
        GRID_W = 64
        GRID_H = 64
        WORLD_EXTENT = 1000

        #Rasterizer
        rasterizer = MapRasterizer(grid_width=GRID_W, grid_height=GRID_H, world_extent=WORLD_EXTENT)
        
        #Returns the format { "globals": ..., "entities": [...] }
        full_world_data = rasterizer.rasterize_to_json(new_state.graph)
        
        print(f"[{task_id}] Rasterization complete. Entities: {len(full_world_data['entities'])}")

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = full_world_data

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"[{task_id}] Map generation failed: {e}\n{error_details}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = {"error": str(e), "details": error_details}
    finally:
        #print(f"[{task_id}] Task finished.")
        pass

@app.post("/generate-map", response_model=Dict[str, str])
async def generate_map(request: GenerateRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}
    background_tasks.add_task(run_world_generation_task, task_id, request.prompt)
    return {"task_id": task_id}

@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "status": tasks[task_id]["status"],
        "result": tasks[task_id]["result"]
    }

@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.post("/reset")
async def reset_world():
    #Clears history to start a fresh Genesis
    core.history = []
    core.current_step = -1
    return {"message": "World reset successfully"}

@app.post("/undo", response_model=TaskStatus)
async def undo_step():
    #Moves the history pointer back one step and returns the previous world
    core.undo()
    
    current_state = core.get_current_state()
    if not current_state:
        raise HTTPException(status_code=400, detail="Cannot undo any further (or no world exists).")
    
    #Re-rasterize the previous state to show it on the frontend
    GRID_W = 64
    GRID_H = 64
    WORLD_EXTENT = 1000
    rasterizer = MapRasterizer(grid_width=GRID_W, grid_height=GRID_H, world_extent=WORLD_EXTENT)
    full_world_data = rasterizer.rasterize_to_json(current_state.graph)

    return {
        "task_id": "undo-action",
        "status": "completed",
        "result": full_world_data
    }

@app.post("/redo", response_model=TaskStatus)
async def redo_step():
    #Moves the history pointer forward one step
    core.redo()
    
    current_state = core.get_current_state()
    if not current_state:
        raise HTTPException(status_code=400, detail="Cannot redo (at latest step).")

    GRID_W = 64
    GRID_H = 64
    WORLD_EXTENT = 1000
    rasterizer = MapRasterizer(grid_width=GRID_W, grid_height=GRID_H, world_extent=WORLD_EXTENT)
    full_world_data = rasterizer.rasterize_to_json(current_state.graph)

    return {
        "task_id": "redo-action",
        "status": "completed",
        "result": full_world_data
    }