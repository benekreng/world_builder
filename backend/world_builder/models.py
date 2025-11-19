from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

Category = Literal[
    "Settlement",
    "River",
    "Lake",
    "MountainRange",
    "Road",
    "Marsh",
    "Forest",
    "Region",
    "Landmark",
    "Field"
]

RelationType = Literal[
    "north_of",
    "south_of",
    "east_of",
    "west_of",
    "near",
    "adjacent_to",
    "distance",
    "flows_into",
    "part_of",
    "between"
]

# Same here
# class Relation(BaseModel):
#     type: RelationType = Field(description="Type of relationship to another feature, e.g. 'north_of', 'distance', etc.")
#     target: str = Field(description="The feature ID this relation connects to.")
#     value: Optional[Any] = Field(
#         default=None,
#         description="Optional raw value associated with the relation, "
#                     "such as '3-day walk'. Not used for coordinates."
#     )

# class Vec2(BaseModel):
#     x: float = Field(description="X coordinate between 0 and 1000.")
#     y: float = Field(description="Y coordinate between 0 and 1000.")


# class Geometry(BaseModel):
#     kind: Literal["circle"] = Field(description="Geometry type. Prototype only supports 'circle'.")
#     radius: float = Field(description="Radius of the circle in map units. Depends on feature category.")

# class Feature(BaseModel):
#     id: str = Field(description="Unique identifier for the feature, e.g. 'f1'.")
#     name: str = Field(description="Human-readable name of the feature, extracted from text.")
#     category: Category = Field(description="Geographic category of the feature (Settlement, Lake, Forest, etc.).")
#     attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata extracted from the text (optional).")
#     relations: List[Relation] = Field(default_factory=list, description="List of relational constraints referencing other features.")

#     position: Optional[Vec2] = Field(default=None, description="The (x,y) map coordinate assigned during the coordinate-placement stage.")
#     geometry: Optional[Geometry] = Field(default=None, description="Geometry representation (circle w/ radius) assigned during the placement stage.")

# class FeatureGraph(BaseModel):
#     features: List[Feature] = Field(description="All extracted geographic features and their relations.")


### Focused for the first model pass where we just extract relations
class ExtractRelation(BaseModel):
    type: RelationType = Field(description="Type of relationship to another feature.")
    target: str = Field(description="ID of the feature this relation points to.")
    value: Optional[Any] = Field(default=None, description="Additional relation value such as raw distance or modifier.")


class ExtractFeature(BaseModel):
    id: str = Field(description="Unique identifier for the extracted feature.")
    name: str = Field(description="Name of the feature as described in the text.")
    category: Category = Field(description="Category of the geographic feature.")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata extracted from the text.")
    relations: List[ExtractRelation] = Field(default_factory=list, description="List of relationships to other features.")


class ExtractFeatureGraph(BaseModel):
    features: List[ExtractFeature] = Field(description="List of all extracted features and their relations.")



### Focused model for coordinates, we ask the model to create coordinates for the json we do with the model above. Later we combine the 2.
### This saves tokens and lets us more quickly regenerate coordinates or generate multiple sized candidates at the same time (maybe to avg them)
class Vec2(BaseModel):
    x: float = Field(description="X coordinate between 0 and 1000.")
    y: float = Field(description="Y coordinate between 0 and 1000.")


class CircleGeometry(BaseModel):
    kind: Literal["circle"] = Field(description="Geometry type; prototype only supports 'circle'.")
    radius: float = Field(description="Radius of the circle for this feature based on category type.")


class CoordinateFeatureUpdate(BaseModel):
    position: Optional[Vec2] = Field(default=None, description="Optional 2D position for a feature's center.")
    geometry: Optional[CircleGeometry] = Field(default=None, description="Optional circular geometry for a feature.")


class CoordinateUpdateModel(BaseModel):
    positions: Dict[str, Vec2] = Field(default_factory=dict, description="Mapping of feature IDs to their positions.")
    geometries: Dict[str, CircleGeometry] = Field(default_factory=dict, description="Mapping of feature IDs to their geometries.")


## Final graph with both of the above combined
class FinalFeature(BaseModel):
    id: str = Field(description="Unique identifier of the feature.")
    name: str = Field(description="Name of the feature as described in the text.")
    category: Category = Field(description="Category classification of the feature.")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the feature.")
    relations: List[ExtractRelation] = Field(default_factory=list, description="Relational constraints to other features.")

    position: Optional[Vec2] = Field(default=None, description="Final assigned position of the feature, if any.")
    geometry: Optional[CircleGeometry] = Field(default=None, description="Final assigned geometry of the feature, if any.")


class FinalFeatureGraph(BaseModel):
    features: List[FinalFeature] = Field(description="List of all features with optional coordinates and geometry.")

