import React, { Component } from "react";
import ExperienceCard from "../../components/experienceCard/ExperienceCard.js";
import Accordion from "react-bootstrap/Accordion";
import "./ExperienceAccordion.css";

class ExperienceAccordion extends Component {
  render() {
    const theme = this.props.theme;
    const headerStyle = {
      backgroundColor: theme.body,
      border: "1px solid",
      borderRadius: "5px",
      borderColor: theme.headerColor,
      marginBottom: "3px",
      fontFamily: "Google Sans Regular",
      color: theme.text,
      cursor: "pointer",
    };

    const headerHoverStyle = {
      color: theme.secondaryText,
    };

    //TODO Change Style

    return (
      <div className="experience-accord">
        <Accordion defaultActiveKey="0">
          {this.props.sections.map((section, sectionIndex) => {
            return (
              <Accordion.Item eventKey={section["title"]} key={sectionIndex}>
                <Accordion.Header
                  className="accordion-header"
                  style={headerStyle}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.color = headerHoverStyle.color)
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.color = headerStyle.color)
                  }
                >
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
