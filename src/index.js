import React from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "styletron-react";
import { Client } from "styletron-engine-atomic";

import "./index.css";
import "bootstrap/dist/css/bootstrap.min.css";
import App from "./App";
import * as serviceWorker from "./serviceWorker";
import "./assets/font-awesome/css/all.css";

const engine = new Client();

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <Provider value={engine}>
    <App />
  </Provider>,
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
