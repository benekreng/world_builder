import type { WorldDto } from "./world.dto";
import type { World, WorldObject } from "./world";

export function mapToWorld(worldDto: WorldDto): World {
    const { x: width, y: height } = worldDto.globals.cell_resolution;

    const objects: WorldObject[] = [];

    for (const entity of worldDto.entities) {
        const entityName: string | null = entity.metadata?.name ?? null;

        for (const cell of entity.cells) {
            objects.push({
                id: entity.id,
                kind: cell.prop.name,
                name: entityName,
                x: cell.x,
                y: cell.y,
                part: cell.prop.part,
            });
        }
    }

    const world: World = {
        width,
        height,
        tiles: [],
        objects,
    };

    return world;
}