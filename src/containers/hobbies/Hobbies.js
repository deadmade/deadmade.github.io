import React from "react";
import "./Hobbies.css";
import HobbySection from "./HobbySection";
import { Fade } from "react-reveal";

export default function Hobbies(props) {
  const theme = props.theme;
  return (
    <div className="main" id="hobbies">
      <div className="hobbies-header-div">
        <Fade bottom duration={2000} distance="20px">
          <h1 className="hobbies-header" style={{ color: theme.text }}>
            Meine Hobbys und Interessen
          </h1>
        </Fade>
      </div>
      <HobbySection theme={theme} />
    </div>
  );
}
