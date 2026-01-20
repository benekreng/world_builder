export interface WorldDto {
  globals: {
    cell_resolution: {
      x: number;
      y: number;
    };
  };
  entities: EntityDto[];
}

export interface EntityDto {
  id: string;
  category: string;
  metadata?: {
    name?: string;
    description?: string;
    color?: string;
    [key: string]: any;
  };
  cells: CellDto[];
}

export interface CellDto {
  x: number;
  y: number;
  prop: {
    name: string;
    part: number;
  };
}