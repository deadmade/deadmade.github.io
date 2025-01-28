import React, { Component } from "react";
import ExperienceCard from "../../components/experienceCard/ExperienceCard.js";
import Accordion from "react-bootstrap/Accordion";
import "./ExperienceAccordion.css";

class ExperienceAccordion extends Component {
  render() {
    const theme = this.props.theme;

    return (
      <div className="experience-accord">
        <Accordion defaultActiveKey="0">
          {this.props.sections.map((section, sectionIndex) => {
            return (
              <Accordion.Item eventKey={section["title"]} key={sectionIndex}>
                <Accordion.Header className="accordion-header">
                  {section["title"]}
                </Accordion.Header>
                <Accordion.Body style={{ backgroundColor: theme.body }}>
                  {section["experiences"].map((experience, index) => {
                    return (
                      <ExperienceCard
                        key={index}
                        index={index}
                        totalCards={section["experiences"].length}
                        experience={experience}
                        theme={theme}
                      />
                    );
                  })}
                </Accordion.Body>
              </Accordion.Item>
            );
          })}
        </Accordion>
      </div>
    );
  }
}

export default ExperienceAccordion;
