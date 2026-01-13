import type { WorldDto } from "../world.dto";

interface GenerateMapResponse {
  taskId: string;
}

type GenerateMapStatusResponse =
  | {
      status: "processing";
      result: null;
    }
  | {
      status: "completed";
      result: WorldDto;
    }
  | {
      status: "failed";
      result: string; // error message
    };

export class Client {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async triggerWorldGeneration(prompt: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/generate-map`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    if (!response.ok) {
      throw new Error("Failed to start map generation");
    }

    const data = (await response.json()) as GenerateMapResponse;

    return data.taskId;
  }

  async getGeneratedWorld(taskId: string): Promise<WorldDto> {
    while (true) {
      const response = await fetch(`${this.baseUrl}/tasks/${taskId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch status for task ${taskId}`);
      }

      const data = (await response.json()) as GenerateMapStatusResponse;

      if (data.status === "completed") {
        return data.result;
      }

      if (data.status === "failed") {
        throw new Error(`Map generation for task ${taskId} failed`);
      }

      if (data.status === "processing") {
        await this.sleep(10000);
      }

      throw new Error(`Invalid status received`);
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}