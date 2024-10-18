import React, { Component } from "react";
import "./Issues.css";
import { Slide } from "react-awesome-reveal";
import IssueCard from "../../components/issueCard/IssueCard";
import issuesData from "../../shared/opensource/issues.json";

class Issues extends Component {
  render() {
    const theme = this.props.theme;
    return (
      <div>
        <div className="issues-header-div">
          <Slide direction="up" duration={2000} triggerOnce>
            <h1 className="issues-header" style={{ color: theme.text }}>
              Issues
            </h1>
          </Slide>
        </div>
        <div className="issues-body-div">
          {issuesData["data"].map((issue) => {
            return <IssueCard issue={issue} />;
          })}
        </div>
      </div>
    );
  }
}

export default Issues;
