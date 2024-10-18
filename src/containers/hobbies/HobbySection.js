import React, { Component } from "react";
import "./Hobbies.css";
import { hobbies } from "../../portfolio";
import { Fade } from "react-reveal";
import SoftwareSkill from "../../components/softwareSkills/SoftwareSkill";
import DesignImg from "./DesignImg";
import FitnessStats from "./FitnessStats";
import ReadingBooks from "./Reading";


function GetSkillSvg(props) {
  if (props.fileName === "FitnessStats")
    return <FitnessStats theme={props.theme} />;
  else if (props.fileName === "ReadingBooks")
    return <ReadingBooks theme={props.theme} />;
  return <DesignImg theme={props.theme} />;
}

class HobbySection extends Component {
  render() {
    const theme = this.props.theme;
    return (
      <div>
        {hobbies.data.map((hobby, i) => {
          return (
            <div key={i} className="hobbies-main-div">
                <Fade left duration={2000}>
                <div className="skills-image-div">
                  <GetSkillSvg fileName={hobby.fileName} theme={theme} />
                </div>
              </Fade>

              <div className="hobbies-text-div">
                <Fade right duration={1000}>
                  <h1 className="hobbies-heading" style={{ color: theme.text }}>
                    {hobby.title}
                  </h1>
                </Fade>
                <Fade right duration={1500}>
                  <SoftwareSkill logos={hobby.softwareSkills} />
                </Fade>
                <Fade right duration={1500}>
                  <div>
                    {hobby.descriptions.map((hobbySentence, i) => {
                      return (
                        <p
                          key={i}
                          className="subTitle hobbies-text"
                          style={{ color: theme.secondaryText }}
                        >
                          {hobbySentence}
                        </p>
                      );
                    })}
                  </div>
                </Fade>
              </div>
            </div>
          );
        })}
      </div>
    );
  }
}

export default HobbySection;
