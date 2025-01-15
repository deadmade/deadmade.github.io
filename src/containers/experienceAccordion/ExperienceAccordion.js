import React, { Component } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import Card from 'react-bootstrap/Card';
import ExperienceCard from "../../components/experienceCard/ExperienceCard.js";

class ExperienceAccordion extends Component {
  render() {
    const theme = this.props.theme;
    return (
      <div className="experience-accord">
        <Accordion defaultActiveKey="0">
          {this.props.sections.map((section, sectionIndex) => {
            return (
              <Card key={section["title"]}>
                <Card.Header>
                  <Accordion.Toggle as={Card.Header} eventKey={sectionIndex.toString()}>
                    {section["title"]}
                  </Accordion.Toggle>
                </Card.Header>
                <Accordion.Collapse eventKey={sectionIndex.toString()}>
                  <Card.Body style={{ backgroundColor: theme.body }}>
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
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
            );
          })}
        </Accordion>
      </div>
    );
  }
}

export default ExperienceAccordion;