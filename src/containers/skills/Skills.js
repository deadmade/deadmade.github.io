import React from "react";
import "./Skills.css";
import SkillSection from "./SkillSection";
import { Slide } from "react-awesome-reveal";

export default function Skills(props) {
  const theme = props.theme;
  return (
    <div className="main" id="skills">
      <div className="skills-header-div">
        <Slide direction="up" duration={2000} triggerOnce>
          <h1 className="skills-header" style={{ color: theme.text }}>
          Womit ich mich beschäftige
          </h1>
        </Slide>
      </div>
      <SkillSection theme={theme} />
    </div>
  );
}
