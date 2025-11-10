// Types for our experimental world

export type TileType = "ground" | "water" | "mountain" | "field";

export interface Tile {
  x: number;          // grid column index
  y: number;          // grid row index
  type: TileType;     // semantic terrain type
}

export interface WorldObject {
  id: string;
  kind: "city" | "tree" | "rock" | "mountain" | "water" | "special";
  name?: string;
  x: number;          // grid position (same units as tiles)
  y: number;
}

export interface World {
  width: number;      // in tiles
  height: number;     // in tiles
  tiles: Tile[];
  objects: WorldObject[];
}

// ---- MOCK DATA ----
// Edit this however you like to test visuals.

const WIDTH = 24;
const HEIGHT = 14;

const tiles: Tile[] = [];

// Simple example terrain:
// - water border
// - some mountains band
// - some fields
for (let y = 0; y < HEIGHT; y++) {
  for (let x = 0; x < WIDTH; x++) {
    let type: TileType = "ground";

    // water border
    if (x === 0 || y === 0 || x === WIDTH - 1 || y === HEIGHT - 1) {
      type = "water";
    }

    // mountain ridge
    if (y === 4 && x > 3 && x < WIDTH - 4) {
      type = "mountain";
    }

    // fields 
    if (y > 8 && x % 3 === 0 && type === "ground") {
      type = "field";
    }


    tiles.push({ x, y, type });
  }
}

const objects: WorldObject[] = [
  { id: "city-1", kind: "city", name: "Harborfall", x: 4, y: 8 },
  { id: "city-2", kind: "city", name: "Highcrest", x: 16, y: 3 },
  { id: "tree-1", kind: "tree", x: 8, y: 9 },
  { id: "tree-2", kind: "tree", x: 9, y: 9 },
  { id: "tree-3", kind: "tree", x: 9, y: 10 },
  { id: "tree-4", kind: "tree", x: 9, y: 10 },
  { id: "tree-5", kind: "tree", x: 9, y: 11 },
  { id: "tree-6", kind: "tree", x: 9, y: 12 },
  { id: "tree-7", kind: "tree", x: 10, y: 9 },
  { id: "tree-8", kind: "tree", x: 10, y: 10 },
  { id: "rock-1", kind: "rock", x: 13, y: 6 },
  { id: "rock-2", kind: "rock", x: 14, y: 6 },
  { id: "rock-3", kind: "rock", x: 15, y: 6 },
  { id: "rock-4", kind: "rock", x: 13, y: 7 },
  { id: "rock-5", kind: "rock", x: 13, y: 8 },
  { id: "rock-6", kind: "rock", x: 16, y: 6 },
  { id: "rock-7", kind: "rock", x: 17, y: 6 },
  { id: "rock-8", kind: "rock", x: 18, y: 6 },
  { id: "rock-9", kind: "rock", x: 18, y: 5 },
  { id: "rock-10", kind: "rock", x: 18, y: 4 },
  { id: "water-1", kind: "water", x: 10, y: 6 },
{ id: "water-2", kind: "water", x: 11, y: 6 },
{ id: "water-3", kind: "water", x: 10, y: 7 },
{ id: "water-4", kind: "water", x: 11, y: 7 },
  { id: "special-1", kind: "special", name: "Crystal Spire", x: 20, y: 6 }
];

export const mockWorld: World = {
  width: WIDTH,
  height: HEIGHT,
  tiles,
  objects,
};
