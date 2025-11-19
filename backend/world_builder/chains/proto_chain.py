from pathlib import Path
from ..models import ExtractFeatureGraph, FinalFeatureGraph, FinalFeature
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from ..models import CoordinateUpdateModel
import json

PROMPT_DIR = Path(__file__).parent.parent / "prompts"
EXTRACT_GEO_RELATIONS = (PROMPT_DIR / "extract_geo_relations.prompt").read_text()
EXTRACT_COORDINATES = (PROMPT_DIR / "coodinate_update_step.prompt").read_text()

class ExtractGeoRelations:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ExtractFeatureGraph)

        self.prompt = PromptTemplate(
            template=EXTRACT_GEO_RELATIONS + "\n\n{format_instructions}\n\nInput:\n{world_state_text}",
            input_variables=["world_state_text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    async def run(self, world_state_text: str) ->  ExtractFeatureGraph:
        final_prompt = self.prompt.format(world_state_text=world_state_text)
        response = await self.llm.ainvoke(final_prompt)
        return self.parser.parse(response.content)

class CoordinateUpdateStep:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=CoordinateUpdateModel)

        
        self.prompt = PromptTemplate(

            template=EXTRACT_COORDINATES + 
                "\n\n{format_instructions}\n\nInput Geo Relations:\n{geo_relation_graph}\n\nInput World State Text:\n{world_state_text}",

            input_variables=["geo_relation_graph", "world_state_text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    async def run(self, geo_relation_graph: str, world_state_text: str) ->  CoordinateUpdateModel:
        final_prompt = self.prompt.format(geo_relation_graph=geo_relation_graph, world_state_text=world_state_text)
        response = await self.llm.ainvoke(final_prompt)
        return self.parser.parse(response.content)


# Merge ExtractFeatureGraph with coordinates from coordinateupdatestep into finalfeaturegraph 
def apply_coordinate_updates(graph: FinalFeatureGraph, updates: CoordinateUpdateModel) -> FinalFeatureGraph:
    # Index by ID for easy access
    features_by_id = {f.id: f for f in graph.features}

    # Apply positions
    for fid, pos in updates.positions.items():
        if fid in features_by_id:
            features_by_id[fid].position = pos

    # Apply geometries
    for fid, geom in updates.geometries.items():
        if fid in features_by_id:
            features_by_id[fid].geometry = geom

    return graph


def promote_extracted_to_final(extracted: ExtractFeatureGraph) -> FinalFeatureGraph:
    final_features = []

    for feature in extracted.features:
        final_features.append(
            FinalFeature(
                id=feature.id,
                name=feature.name,
                category=feature.category,
                attributes=feature.attributes,
                relations=feature.relations,
                position=None,
                geometry=None
            )
        )

    return FinalFeatureGraph(features=final_features)


class MapPipeline:
    def __init__(self, llm):
        self.llm = llm
        self.extract_geo_relations = ExtractGeoRelations(llm)
        self.coordinate_update_step = CoordinateUpdateStep(llm)
    
    async def run(self, world_state_text):
        print("Extracting Geo Features...")
        geo = await self.extract_geo_relations.run(world_state_text)
        print("Update coordinates...")
        coord_updates = await self.coordinate_update_step.run(geo.model_dump_json(), world_state_text)
        # TODO: update world_state_text at the same time as coordinate_update_setp

        final_feature_graph = promote_extracted_to_final(geo)
        final_graph = apply_coordinate_updates(final_feature_graph, coord_updates)
        return final_graph