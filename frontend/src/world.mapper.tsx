import type { WorldDto } from "./world.dto";
import type { World, WorldObject, TileType } from "./world";
import { createBaseGrid } from "./world";

const TERRAIN_PROPS = new Set(["ground", "water", "field", "path", "sand", "snow", "mountain", "swamp"]);

const DEFAULT_W = 64;
const DEFAULT_H = 64;

export function mapToWorld(worldDto: WorldDto): World {
    //Get dimensions or default to 64x64
    const width = worldDto.globals?.cell_resolution?.x ?? DEFAULT_W;
    const height = worldDto.globals?.cell_resolution?.y ?? DEFAULT_H;

    //Initialize the Base Grid with default "ground"
    const tiles = createBaseGrid(width, height)

    const objects: WorldObject[] = [];
    const meta: Record<string, any> = {};

    //Access the flat tiles array
    const setTile = (x: number, y: number, type: TileType, id: string) => {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            const t = tiles[y * width + x];
            t.type = type;
            t.entityId = id;
        }
    };

    //Process every cell from the backend
    for (const entity of worldDto.entities) {
        meta[entity.id] = entity.metadata || {};

        for (const cell of entity.cells) {
            const propName = cell.prop.name;

            if (TERRAIN_PROPS.has(propName)) {
                setTile(cell.x, cell.y, propName as TileType, entity.id);
            } 
            else if (propName === "bridge") {
                setTile(cell.x, cell.y, "water", entity.id);
                objects.push({
                    id: entity.id,
                    kind: propName,
                    name: entity.metadata?.name ?? null,
                    x: cell.x,
                    y: cell.y,
                    part: cell.prop.part,
                });
            }
            else {
                objects.push({
                    id: entity.id,
                    kind: propName,
                    name: entity.metadata?.name ?? null,
                    x: cell.x,
                    y: cell.y,
                    part: cell.prop.part,
                });
            }
        }
    }

    return { width, height, tiles, objects, meta };
}