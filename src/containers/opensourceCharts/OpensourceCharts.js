import React, { Component } from "react";
import PullRequestChart from "../../components/pullRequestChart/PullRequestChart.js";
import IssueChart from "../../components/issueChart/IssueChart.js";
import { Slide } from "react-awesome-reveal";
import "./OpensourceCharts.css";

class OpensourceCharts extends Component {
  render() {
    const theme = this.props.theme;
    return (
      <div className="main-div">
        <div className="os-charts-header-div">
          <Slide direction="up" duration={2000} triggerOnce>
            <h1 className="os-charts-header" style={{ color: theme.text }}>
              Contributions
            </h1>
          </Slide>
        </div>
        <div className="os-charts-body-div">
          <PullRequestChart />
          <IssueChart />
        </div>
      </div>
    );
  }
}

export default OpensourceCharts;
