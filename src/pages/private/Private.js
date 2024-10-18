import React, { Component } from "react";
import Header from "../../components/header/Header";
import Hobbies from "../../containers/hobbies/Hobbies";
import Footer from "../../components/footer/Footer";
import TopButton from "../../components/topButton/TopButton";

class Private extends Component {
  render() {
    return (
      <div>
        <Header theme={this.props.theme} />
        <Hobbies theme={this.props.theme} />
        <Footer theme={this.props.theme} />
        <TopButton theme={this.props.theme} />
      </div>
    );
  }
}

export default Private;
