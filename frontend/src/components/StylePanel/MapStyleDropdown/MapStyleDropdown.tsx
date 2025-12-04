import React, { useState } from "react";
import type { WorldStyle } from "../../../App";
import "../StylePanel.css";
import "./MapStyleDropdown.css";


interface MapStyleDropdownProps {
  value: WorldStyle;
  onChange: (style: WorldStyle) => void;
}

interface StyleOption {
  id: WorldStyle;
  label: string;
  description: string;
  image: string;
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

export const MapStyleDropdown: React.FC<MapStyleDropdownProps> = ({
  value,
  onChange,
}) => {
  const [open, setOpen] = useState(false);

  const currentOption =
    STYLE_OPTIONS.find((opt) => opt.id === value) ?? STYLE_OPTIONS[0];

  const handleSelect = (id: WorldStyle) => {
    onChange(id);
    setOpen(false);
  };

  return (
    <div className="style-dropdown">
      <button
        type="button"
        className="style-dropdown-button"
        onClick={() => setOpen((prev) => !prev)}
      >
        <div
          className="style-dropdown-preview"
          style={{ backgroundImage: `url(${currentOption.image})` }}
        >
          <div className="style-dropdown-overlay">
            <div className="style-dropdown-label">{currentOption.label}</div>
            <div className="style-dropdown-description">
              {currentOption.description}
            </div>
          </div>
        </div>
        <span className="style-dropdown-caret">
          {open ? "▲" : "▼"}
        </span>
      </button>

      {open && (
        <div className="style-dropdown-menu">
          {STYLE_OPTIONS.map((option) => (
            <button
              key={option.id}
              type="button"
              className={`style-dropdown-option ${
                option.id === value
                  ? "style-dropdown-option--active"
                  : ""
              }`}
              onClick={() => handleSelect(option.id)}
            >
              <div
                className="style-option-bg"
                style={{ backgroundImage: `url(${option.image})` }}
              >
                <div className="style-option-overlay">
                  <div className="style-option-label">{option.label}</div>
                  <div className="style-option-description">
                    {option.description}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
