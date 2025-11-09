import type { WorldStyle } from "../../App";
import "./StylePanel.css";

interface StylePanelProps {
  worldStyle: WorldStyle;
  onChangeStyle: (style: WorldStyle) => void;
}

interface StyleOption {
  id: WorldStyle;
  label: string;
  description: string;
  image: string; // path to tile image
}

const STYLE_OPTIONS: StyleOption[] = [
  {
    id: "earth",
    label: "Earth",
    description: "Lush forests, oceans, familiar landscapes.",
    image: "/src/assets/style-earth.jpg",
  },
  {
    id: "mars",
    label: "Mars",
    description: "Red deserts, craters, harsh rock formations.",
    image: "/src/assets/style-mars.jpg",
  },
  {
    id: "fantasy",
    label: "Fantasy",
    description: "Floating islands, forests, enchanted realms.",
    image: "/src/assets/style-fantasy.jpg",
  },
  {
    id: "scifi",
    label: "Sci-Fi",
    description: "Neon cities, holograms, futuristic grids.",
    image: "/src/assets/style-scifi.jpg",
  },
];

export const StylePanel: React.FC<StylePanelProps> = ({
  worldStyle,
  onChangeStyle,
}) => {
  return (
    <aside className="style-panel">
      <h2 className="style-panel-title">Map Style</h2>
      <p className="style-panel-subtitle">
        Choose a visual theme. The generated structure stays the same.
      </p>

      <div className="style-grid">
        {STYLE_OPTIONS.map((option) => {
          const isActive = option.id === worldStyle;
          return (
            <button
              key={option.id}
              type="button"
              className={`style-tile ${isActive ? "style-tile--active" : ""}`}
              onClick={() => onChangeStyle(option.id)}
            >
              <div
                className="style-tile-bg"
                style={{ backgroundImage: `url(${option.image})` }}
              />
              <div className="style-tile-overlay">
                <div className="style-tile-label">{option.label}</div>
                <div className="style-tile-description">
                  {option.description}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
};
