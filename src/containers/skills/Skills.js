import React from "react";
import "./Skills.css";
import SkillSection from "./SkillSection";
import { Fade } from "react-swift-reveal";

export default function Skills(props) {
  const theme = props.theme;
  return (
    <div className="main" id="skills">
      <div className="skills-header-div">
        <Fade bottom duration={2000} distance="20px">
          <h1 className="skills-header" style={{ color: theme.text }}>
            Womit ich mich beschäftige
          </h1>
        </Fade>
      </div>
      <SkillSection theme={theme} />
    </div>
  );
}
