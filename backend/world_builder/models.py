# world_builder/models.py
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import uuid4

# ==========================================
# 1. THE SEMANTIC GRAPH (The Source of Truth)
# ==========================================

EntityType = Literal[
    "Settlement", "River", "Lake", "Sea", "MountainRange", 
    "Road", "Marsh", "Forest", "Region", "Landmark", "Field", "Island"
]

RelationType = Literal[
    "Near", "Far", 
    "EastOf", "WestOf", "NorthOf", "SouthOf", 
    "Between", "Inside", "ConnectedTo"
]

class EntityNode(BaseModel):
    id: str = Field(default_factory=lambda: f"ent_{str(uuid4())[:8]}")
    name: str
    type: EntityType
    description: str
    
    # The SOLVER fills these. The LLM does NOT guess these.
    x: float = Field(default=50.0, description="0-100 coordinate")
    y: float = Field(default=50.0, description="0-100 coordinate")
    
    # Metadata for asset selection
    size: Literal["Small", "Medium", "Large"] = "Medium"

class SpatialConstraint(BaseModel):
    source_id: str
    target_id: str
    relation: RelationType
    # stiffness: 0.0 to 1.0. 
    # High = strict distance/connection (Road). Low = general vibe (Near).
    stiffness: float = 0.5 

class MapGraph(BaseModel):
    entities: List[EntityNode] = []
    constraints: List[SpatialConstraint] = []
    
    # Global scale helps the renderer decide if 1 pixel is 1 meter or 1 km
    width_description: str = "Unknown area"

# ==========================================
# 2. STATE MANAGEMENT (History & Time Travel)
# ==========================================

class WorldState(BaseModel):
    """
    A snapshot of the world at a specific point in time.
    This is what we save to the 'undo stack'.
    """
    step_index: int
    narrative: str = Field(description="The running text description of the world.")
    graph: MapGraph
    
    # We keep the last user prompt that created this state for context
    last_user_prompt: str = ""

# ==========================================
# 3. LLM ACTION INTENT (The Mutator)
# ==========================================

class GraphMutation(BaseModel):
    action_type: Literal["ADD", "REMOVE", "MODIFY"]
    
    # For ADD/MODIFY
    entity_data: Optional[EntityNode] = None
    
    # For ADD constraint
    constraint_data: Optional[SpatialConstraint] = None
    
    # For REMOVE/MODIFY lookup
    target_id: Optional[str] = None
    
    rationale: str = Field(description="Why this change is happening.")

class WorldEvolution(BaseModel):
    """The raw output from the LLM when the user types something."""
    updated_narrative: str = Field(description="The rewritten or appended world description.")
    mutations: List[GraphMutation] = Field(description="List of graph operations to perform.")

# ==========================================
# 4. FRONTEND OUTPUT (The PDF Schema)
# ==========================================

class PropData(BaseModel):
    name: str
    part: int = 0

class GridCell(BaseModel):
    x: int
    y: int
    entity_id: Optional[str] = None
    layer: Optional[str] = None
    prop: Optional[PropData] = None

class FrontendEntity(BaseModel):
    id: str
    metadata: Dict[str, Any]
    category: str

class FrontendMapData(BaseModel):
    entities: List[FrontendEntity]
    grid: List[GridCell]