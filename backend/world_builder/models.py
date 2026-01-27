from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid

# --- Types & Enums ---
Category = Literal[
    "Settlement", "River", "Lake", "Sea", "MountainRange",
    "Road", "Marsh", "Forest", "Region", "Landmark", "Field", "Island"
]

RelationType = Literal[
    "north_of",
    "south_of",
    "east_of",
    "west_of",
    "near",
    "adjacent_to",
    "distance",
    "flows_from",
    "flows_within",
    "flows_into",
    "flows_to",
    "part_of",
    "contains",
    "within",
    "between",
    "on",
    "at",
    "across",
    "unknown"
]

#Geometry Definitions
class Vec2(BaseModel):
    x: float = Field(description="X coordinate between 0 and 1000.")
    y: float = Field(description="Y coordinate between 0 and 1000.")

class CircleGeometry(BaseModel):
    kind: Literal["circle"] = Field(description="Geometry type for point-like features.")
    radius: float = Field(description="Radius of the circle.")

class SpineNode(BaseModel):
    position: Vec2 = Field(description="Position of this node.")
    radius: float = Field(description="The volume/radius at this specific node.")

class SpineGeometry(BaseModel):
    kind: Literal["spine"] = Field(description="Geometry for areas/lines.")
    nodes: List[SpineNode] = Field(description="Nodes defining the spine and its volume.")

#Extraction Models
class ExtractRelation(BaseModel):
    type: RelationType = Field(description="Type of relationship.")
    target: str = Field(description="ID of target feature.")
    value: Optional[Any] = Field(default=None)

class ExtractFeature(BaseModel):
    id: str = Field(description="Unique identifier, e.g., 'f1'.")
    name: str = Field(description="Name of the feature.")
    category: Category = Field(description="Category.")
    attributes: Dict[str, Any] = Field(default_factory=dict)
    relations: List[ExtractRelation] = Field(default_factory=list)

class ExtractFeatureGraph(BaseModel):
    features: List[ExtractFeature]

#Update Models
class CoordinateUpdateModel(BaseModel):
    positions: Dict[str, Vec2] = Field(
        default_factory=dict, 
        description="Map feature IDs (e.g. 'f1') to their center coordinates."
    )
    geometries: Dict[str, Union[CircleGeometry, SpineGeometry]] = Field(
        default_factory=dict, 
        description="Map feature IDs to their specific shape (Circle or Spine)."
    )

#Final Combined Models
class FinalFeature(BaseModel):
    id: str
    name: str
    category: Category
    attributes: Dict[str, Any] = Field(default_factory=dict)
    relations: List[ExtractRelation] = Field(default_factory=list)
    position: Optional[Vec2] = None
    geometry: Optional[Union[CircleGeometry, SpineGeometry]] = None

class FinalFeatureGraph(BaseModel):
    features: List[FinalFeature]

#Evolution Schemas
#1. Graph Operations
class OperationType(str, Enum):
    ADD = "add"
    EDIT = "edit"
    REMOVE = "remove"

class AddFeatureOp(BaseModel):
    action: Literal[OperationType.ADD]
    feature: FinalFeature

class EditFeatureOp(BaseModel):
    action: Literal[OperationType.EDIT]
    id: str
    changes: Dict[str, Any]

class RemoveFeatureOp(BaseModel):
    action: Literal[OperationType.REMOVE]
    id: str

GraphOperation = Union[AddFeatureOp, EditFeatureOp, RemoveFeatureOp]

#2. LLM Response Wrappers
class GenesisResponse(BaseModel):
    """Output for the Initial Generation (Phase A)"""
    fluid_ground_truth: str = Field(..., description="A thorough, novelistic description of the world state.")
    initial_graph: FinalFeatureGraph = Field(..., description="The complete initial graph structure.")

class EvolutionResponse(BaseModel):
    """Output for the Update Loop (Phase B)"""
    updated_fluid_ground_truth: str = Field(..., description="The rewritten fluid text incorporating user changes.")
    graph_updates: List[GraphOperation] = Field(..., description="List of operations to update the graph.")

#3. State Container for History
class WorldState(BaseModel):
    #The Object stored in the WorldBuilder History
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    fluid_truth: str
    graph: FinalFeatureGraph
    prompt: str = ""
    step_type: str = "genesis"