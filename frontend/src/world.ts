import type { WorldDto } from "./world.dto";
import * as Mapper from "./world.mapper";

export type TileType = "ground" | "water" | "mountain" | "field" | "path";

export interface Tile {
  x: number;         
  y: number;          
  type: TileType;     
}

export interface WorldObject {
  id: string;
  kind: string;
  name: string | null;
  x: number;          
  y: number;
  part: number;
}

export interface World {
  width: number;      
  height: number;     
  tiles: Tile[];
  objects: WorldObject[];
}

const WIDTH = 64;
const HEIGHT = 32;

const tiles: Tile[] = [];

for (let y = 0; y < HEIGHT; y++) {
  for (let x = 0; x < WIDTH; x++) {
    tiles.push({ x, y, type: "ground" });
  }
}

const TILE_OVERRIDES: Array<{ x: number; y: number; type: TileType }> = [
  { x: 9, y: 20, type: "water" },
  { x: 9, y: 21, type: "water" },
  { x: 9, y: 22, type: "water" },
  { x: 9, y: 23, type: "water" },
  { x: 9, y: 24, type: "water" },
  { x: 9, y: 25, type: "water" },
  { x: 9, y: 26, type: "water" },
  { x: 9, y: 27, type: "water" },
  { x: 9, y: 28, type: "water" },
  { x: 9, y: 29, type: "water" },
  { x: 9, y: 30, type: "water" },
  { x: 9, y: 31, type: "water" },
  { x: 8, y: 20, type: "water" },
  { x: 8, y: 21, type: "water" },
  { x: 8, y: 22, type: "water" },
  { x: 8, y: 23, type: "water" },
  { x: 8, y: 24, type: "water" },
  { x: 8, y: 25, type: "water" },
  { x: 8, y: 26, type: "water" },
  { x: 8, y: 27, type: "water" },
  { x: 8, y: 28, type: "water" },
  { x: 8, y: 29, type: "water" },
  { x: 8, y: 30, type: "water" },
  { x: 8, y: 31, type: "water" },
  { x: 7, y: 20, type: "water" },
  { x: 7, y: 21, type: "water" },
  { x: 7, y: 22, type: "water" },
  { x: 7, y: 23, type: "water" },
  { x: 7, y: 24, type: "water" },
  { x: 7, y: 25, type: "water" },
  { x: 7, y: 26, type: "water" },
  { x: 7, y: 27, type: "water" },
  { x: 7, y: 28, type: "water" },
  { x: 7, y: 29, type: "water" },
  { x: 7, y: 30, type: "water" },
  { x: 6, y: 21, type: "water" },
  { x: 6, y: 22, type: "water" },
  { x: 6, y: 23, type: "water" },
  { x: 6, y: 24, type: "water" },
  { x: 6, y: 25, type: "water" },
  { x: 6, y: 26, type: "water" },
  { x: 6, y: 27, type: "water" },
  { x: 6, y: 28, type: "water" },
  { x: 6, y: 29, type: "water" },
  { x: 5, y: 22, type: "water" },
  { x: 5, y: 23, type: "water" },
  { x: 5, y: 24, type: "water" },
  { x: 5, y: 25, type: "water" },
  { x: 5, y: 26, type: "water" },
  { x: 5, y: 27, type: "water" },
  { x: 5, y: 28, type: "water" },
  { x: 4, y: 23, type: "water" },
  { x: 4, y: 24, type: "water" },
  { x: 4, y: 25, type: "water" },
  { x: 4, y: 26, type: "water" },
  { x: 10, y: 21, type: "water" },
  { x: 10, y: 22, type: "water" },
  { x: 10, y: 23, type: "water" },
  { x: 10, y: 24, type: "water" },
  { x: 10, y: 25, type: "water" },
  { x: 10, y: 26, type: "water" },
  { x: 10, y: 27, type: "water" },
  { x: 10, y: 28, type: "water" },
  { x: 10, y: 29, type: "water" },
  { x: 10, y: 30, type: "water" },
  { x: 11, y: 22, type: "water" },
  { x: 11, y: 23, type: "water" },
  { x: 11, y: 24, type: "water" },
  { x: 11, y: 25, type: "water" },
  { x: 11, y: 26, type: "water" },
  { x: 11, y: 27, type: "water" },
  { x: 11, y: 28, type: "water" },
  { x: 11, y: 29, type: "water" },
  { x: 12, y: 22, type: "water" },
  { x: 12, y: 23, type: "water" },
  { x: 12, y: 24, type: "water" },
  { x: 12, y: 25, type: "water" },
  { x: 12, y: 26, type: "water" },
  { x: 12, y: 27, type: "water" },
  { x: 12, y: 28, type: "water" },
  { x: 12, y: 29, type: "water" },
  { x: 13, y: 23, type: "water" },
  { x: 13, y: 24, type: "water" },
  { x: 13, y: 25, type: "water" },
  { x: 13, y: 26, type: "water" },
  { x: 13, y: 27, type: "water" },
  { x: 13, y: 28, type: "water" },
  { x: 14, y: 23, type: "water" },
  { x: 14, y: 24, type: "water" },
  { x: 14, y: 25, type: "water" },
  { x: 14, y: 26, type: "water" },
  { x: 14, y: 27, type: "water" },
  { x: 15, y: 24, type: "water" },
  { x: 15, y: 25, type: "water" },
  { x: 15, y: 26, type: "water" },
  { x: 16, y: 24, type: "water" },
  { x: 16, y: 25, type: "water" },
  { x: 17, y: 24, type: "water" },
  { x: 17, y: 25, type: "water" },
  { x: 18, y: 24, type: "water" },
  { x: 18, y: 23, type: "water" },
  { x: 18, y: 22, type: "water" },
  { x: 19, y: 22, type: "water" },
  { x: 20, y: 22, type: "water" },
  { x: 21, y: 22, type: "water" },
  { x: 23, y: 22, type: "water" },
  { x: 24, y: 22, type: "water" },
  { x: 25, y: 22, type: "water" },
  { x: 26, y: 21, type: "water" },
  { x: 26, y: 22, type: "water" },
  { x: 26, y: 23, type: "water" },
  { x: 27, y: 20, type: "water" },
  { x: 27, y: 21, type: "water" },
  { x: 27, y: 22, type: "water" },
  { x: 27, y: 23, type: "water" },
  { x: 27, y: 24, type: "water" },
  { x: 28, y: 19, type: "water" },
  { x: 28, y: 20, type: "water" },
  { x: 28, y: 21, type: "water" },
  { x: 28, y: 22, type: "water" },
  { x: 28, y: 23, type: "water" },
  { x: 28, y: 24, type: "water" },
  { x: 28, y: 25, type: "water" },
  { x: 29, y: 20, type: "water" },
  { x: 29, y: 21, type: "water" },
  { x: 29, y: 22, type: "water" },
  { x: 29, y: 23, type: "water" },
  { x: 29, y: 24, type: "water" },
  { x: 30, y: 21, type: "water" },
  { x: 30, y: 22, type: "water" },
  { x: 30, y: 23, type: "water" },
  { x: 31, y: 22, type: "water" },
  
  { x: 10, y: 5, type: "mountain" },
  { x: 11, y: 5, type: "mountain" },

  { x: 3, y: 12, type: "field" },
];

export const mockWorldDto: WorldDto = {
  globals: {
    cell_resolution: { x: WIDTH, y: HEIGHT },
  },
  entities: [
    {
      id: "Settlement_Harborfall",
      category: "Settlement",
      metadata: { name: "Harborfall" },
      cells: [
        { x: 4, y: 8, prop: { name: "city", part: 0 } },
        { x: 4, y: 9, prop: { name: "city", part: 3 } },
        { x: 3, y: 8, prop: { name: "city", part: 2 } },
        { x: 3, y: 9, prop: { name: "city", part: 1 } },
        { x: 5, y: 9, prop: { name: "city", part: 5 } },

        { x: 8, y: 10, prop: { name: "tree_oak", part: 0 } },
        { x: 9, y: 9, prop: { name: "tree_pine", part: 0 } },
        { x: 7, y: 10, prop: { name: "tree_oak", part: 1 } },
        { x: 9, y: 10, prop: { name: "tree_pine", part: 1 } },
      ],
    },

    {
      id: "Settlement_Highcrest",
      category: "Settlement",
      metadata: { name: "Highcrest" },
      cells: [
        { x: 17, y: 5, prop: { name: "city", part: 2 } },
        { x: 17, y: 6, prop: { name: "city", part: 3 } },
        
        // small forest around Highcrest
        { x: 16, y: 8, prop: { name: "tree_pine", part: 0 } },
        { x: 20, y: 7, prop: { name: "tree_oak", part: 0 } },
        { x: 21, y: 6, prop: { name: "tree_pine", part: 1 } },
      ],
    },

    {
      id: "Settlement_Towerwatch",
      category: "Settlement",
      metadata: { name: "Towerwatch" },
      cells: [
        { x: 40, y: 11, prop: { name: "city", part: 0 } },
        { x: 40, y: 12, prop: { name: "city", part: 3 } },
        { x: 39, y: 11, prop: { name: "city", part: 2 } },
        { x: 39, y: 12, prop: { name: "city", part: 1 } },
        { x: 41, y: 11, prop: { name: "city", part: 4 } },
        { x: 41, y: 12, prop: { name: "city", part: 5 } },
        { x: 38, y: 12, prop: { name: "city", part: 7 } },
        { x: 42, y: 12, prop: { name: "city", part: 5 } },

        // trees around Towerwatch
        { x: 28, y: 13, prop: { name: "tree_oak", part: 0 } },
        { x: 32, y: 13, prop: { name: "tree_pine", part: 0 } },
      ],
    },

    {
      id: "Settlement_Southbay",
      category: "Settlement",
      metadata: { name: "Southbay" },
      cells: [
        { x: 22, y: 24, prop: { name: "city", part: 0 } },
        { x: 22, y: 25, prop: { name: "city", part: 3 } },
        { x: 21, y: 24, prop: { name: "city", part: 2 } },
        { x: 21, y: 25, prop: { name: "city", part: 1 } },
        { x: 23, y: 24, prop: { name: "city", part: 4 } },
        { x: 23, y: 25, prop: { name: "city", part: 5 } },

        // trees south of the city
        { x: 21, y: 27, prop: { name: "tree_oak", part: 0 } },
        { x: 23, y: 27, prop: { name: "tree_pine", part: 0 } },
      ],
    },
  ],
};

export const mockWorld: World = Mapper.mapToWorld(mockWorldDto);

for (const { x, y, type } of TILE_OVERRIDES) {
  const tile = tiles.find(t => t.x === x && t.y === y);
  if (tile) tile.type = type;
}

mockWorld.tiles = tiles;