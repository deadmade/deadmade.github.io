---
title: "Projects — Manuel Schülein"
description: "Three projects drawn as architecture diagrams: fangtype, a VS Code tool for Python type annotations, and the team builds RustLogger and IsoPrüfi."
layout: projects
# the switch above each drawing while it runs: its two visible words and its accessible name (it contains both words)
runbar:
  stop: "stop"
  play: "play"
  name: "stop or play the animation"
projects:
  - name: "fangtype"
    tag: "built alone · Studienarbeit"
    drawing: fangtype
    runkey: "a request"
    summary: "fangtype: two round trips over LSP between VS Code and a language server. First, Python code goes to Jedi, which infers types. They come back as inlay hints, which the developer reviews. When the developer accepts a hint, a second request makes the server write the annotation with libcst and validate it with mypy. The edit comes back to VS Code as type annotations."
    what: "A VS Code tool for Python type annotations. Designed, implemented and tested independently. Jedi and the project's own inference passes infer the types, and the editor shows them as hints. When the developer accepts one, the language server writes the annotation and mypy validates it; a rejected annotation is not written."
    stack:
      - "Python"
      - "TypeScript"
      - "VS Code"
      - "LSP"
      - "pygls"
      - "Jedi"
      - "libcst"
      - "mypy"
    source: "https://github.com/deadmade/fangtype"
  - name: "RustLogger"
    tag: "team build"
    drawing: rustlogger
    runkey: "a log line"
    summary: "RustLogger: a Docker Compose stack. All containers log to syslog; an nginx load balancer spreads the logs over three collectors, which send them through a second nginx load balancer (API key, rate limit) to three forwarding API instances. A simulated sensor source, log-gen and log-sender, sends through the same load balancer. The API indexes through a HAProxy load balancer into a five-node Elasticsearch cluster: container logs into one index, sensor logs into another. Outside Docker, a terminal interface searches both through the API."
    what: "A logging pipeline as a Docker Compose stack. Containers log to syslog, collectors forward the lines through nginx to an API that indexes them into a five-node Elasticsearch cluster. A simulated sensor source feeds a second index, and a terminal interface searches both through the API."
    stack:
      - "Rust"
      - "Actix"
      - "Elasticsearch"
      - "Kibana"
      - "nginx"
      - "HAProxy"
      - "Docker"
    source: "https://github.com/DatenKrakenOrg/RustLogger"
  - name: "IsoPrüfi"
    tag: "team build"
    drawing: isopruefi
    runkey: "a reading or a request"
    summary: "IsoPrüfi: Arduino devices on the north and south sides of the building measure the indoor temperature, buffer readings on an SD card while offline, and publish over MQTT to an external broker. In Docker, a .NET MQTT receiver worker stores the readings in InfluxDB. A second .NET worker pulls the outdoor temperature from a weather API, Open-Meteo or Bright Sky, into InfluxDB. A REST API reads InfluxDB and keeps users and settings in PostgreSQL. A React front end, served by nginx, calls the REST API. Each service runs twice behind Traefik."
    what: "A system that tests how well a building is insulated by comparing indoor and outdoor temperature. Arduino devices on the north and south sides measure inside, a weather API supplies outside, and the readings are recorded and evaluated even when parts of the system fail."
    stack:
      - "ASP.NET Core"
      - "React"
      - "PostgreSQL"
      - "InfluxDB"
      - "MQTT"
      - "Arduino"
      - "Docker"
      - "Traefik"
    source: "https://github.com/deadmade/IsoPruefi"
---
