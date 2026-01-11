from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import Response

from world_builder.app import WorldBuilder

# Initialize FastAPI app
app = FastAPI(
    title="API for World Builder",
    description=""
)

core = WorldBuilder()

# Configure CORS to allow React client (assuming it runs on localhost:3000)
origins = [
    "http://localhost",
    "http://localhost:3000",
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

@app.post("/generate-map")
async def generate_map(request: GenerateRequest):
    final_graph = await core.map_pipeline.run(request.prompt)
    return final_graph.model_dump()

@app.get("/")
async def root():
    await core.test_async()
    return {"message": "Hello World"}