export interface WorldDto {
  globals: {
    cell_resolution: {
      x: number;
      y: number;
    };
  };
  entities: EntityDto[];
}

interface EntityDto {
  id: string;
  category: string;
  metadata?: {
    name?: string;
  };
  cells: CellDto[];
}

interface CellDto {
  x: number;
  y: number;
  prop: {
    name: string;
    part: number;
  };
}