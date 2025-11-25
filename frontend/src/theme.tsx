import assetsMap from "./assets/assetsMap.json";

export type Theme = "earth";

const earthFiles = import.meta.glob("../assets/themes/earth/*.png", {
  eager: true,
  as: "url",
});

const themeFiles: Record<Theme, Record<string, string>> = {
  earth: earthFiles
};

export function getAssetPath(theme: Theme, propName: string, part: number): string | undefined {
  const fileName = (assetsMap as Record<string, string[]>)[propName][part];
  if (!fileName) return undefined;

  // files come like "../assets/themes/earth/rock_L.png"
  const files = themeFiles[theme];
  const entry = Object.entries(files).find(([path]) => path.endsWith("/" + fileName));
  return entry?.[1]; // this is already the built URL string
}