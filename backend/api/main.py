import uuid
import traceback
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from world_builder.app import WorldBuilder
from world_builder.rasterizer import MapRasterizer
from fastapi.responses import JSONResponse

app = FastAPI(title="API for World Builder")

core = WorldBuilder()

tasks: Dict[str, Dict[str, Any]] = {}

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://collectivedetails.org",
    "https://www.collectivedetails.org",
]
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

class HistoryItem(BaseModel):
    id: str
    parent_id: Optional[str]
    prompt: str
    type: str
    is_current: bool

class HistoryResponse(BaseModel):
    nodes: list[HistoryItem]
    current_node_id: Optional[str]

async def run_world_generation_task(task_id: str, prompt: str):
    try:
        #Get Old State
        current_state = core.get_current_state()
        
        if current_state is None:
            print(f"[{task_id}] GENESIS: '{prompt}'")
            await core.create_world(prompt)
        else:
            print(f"[{task_id}] EVOLUTION: '{prompt}'")
            await core.update_world(prompt)
            
        #Get the new state
        new_state = core.get_current_state()
        if not new_state:
            raise Exception("World generation returned no state.")

        print(f"[{task_id}] Rasterizing graph with {len(new_state.graph.features)} features...")
        
        #settings
        GRID_W = 64
        GRID_H = 64
        WORLD_EXTENT = 1000

        rasterizer = MapRasterizer(
            grid_width=GRID_W, 
            grid_height=GRID_H, 
            world_extent=WORLD_EXTENT,
            seed=new_state.seed 
        )
        
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
    core.reset()
    return {"message": "World reset successfully"}

@app.get("/history", response_model=HistoryResponse)
async def get_history():
    return {
        "nodes": core.get_history_meta(),
        "current_node_id": core.current_node_id
    }

@app.get("/history/{node_id}/prompts", response_model=list[str])
async def get_node_prompts(node_id: str):
    return core.get_ancestors(node_id)

@app.post("/history/jump/{node_id}")
async def jump_history(node_id: str):
    success = core.jump_to_node(node_id)
    if not success: 
        raise HTTPException(status_code=404, detail="Node not found")
    
    current_state = core.get_current_state()
    GRID_W = 64
    GRID_H = 64
    WORLD_EXTENT = 1000
    rasterizer = MapRasterizer(
        grid_width=GRID_W, 
        grid_height=GRID_H, 
        world_extent=WORLD_EXTENT, 
        seed=current_state.seed
    )
    full_world_data = rasterizer.rasterize_to_json(current_state.graph)
    return {"result": full_world_data}

@app.delete("/history/{node_id}")
async def delete_history_node(node_id: str):
    core.delete_subtree(node_id)
    return {"message": "Subtree deleted"}

@app.get("/download-world")
async def download_world():
    if not core.root_node_id:
        raise HTTPException(status_code=400, detail="No world to save.")
    
    data = core.save_to_dict()
    return JSONResponse(
        content=data, 
        headers={"Content-Disposition": "attachment; filename=fantasy_world.json"}
    )

@app.post("/upload-world")
async def upload_world(payload: Dict[str, Any]):
    success = core.load_from_dict(payload)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid save file format.")
    
    current_state = core.get_current_state()
    
    GRID_W = 64
    GRID_H = 64
    WORLD_EXTENT = 1000
    rasterizer = MapRasterizer(
        grid_width=GRID_W, 
        grid_height=GRID_H, 
        world_extent=WORLD_EXTENT, 
        seed=current_state.seed
    )
    full_world_data = rasterizer.rasterize_to_json(current_state.graph)

    return {"message": "Loaded", "result": full_world_data}