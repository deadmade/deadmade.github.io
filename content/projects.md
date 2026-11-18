---
title: "Projects — Manuel Schülein"
description: "Three projects drawn as architecture diagrams: fangtype, a VS Code tool for Python type annotations, and the team builds RustLogger and IsoPrüfi."
layout: projects
projects:
  - name: "fangtype"
    tag: "built alone · Studienarbeit"
    drawing: fangtype
    summary: "fangtype: two round trips over LSP between VS Code and a language server. First, Python code goes to Jedi, which infers types. They come back as inlay hints, which the developer reviews. When the developer accepts a hint, a second request makes the server write the annotation with libcst and validate it with mypy. The edit comes back to VS Code as type annotations."
    what: "An LSP server written in Python and a VS Code extension that show the types Jedi infers in Python code as inlay hints and insert them with a code action or, for a whole file, through a separate diff view."
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
    summary: "RustLogger: a Docker Compose stack. All containers log to syslog; an nginx load balancer spreads the logs over three collectors, which send them through a second nginx load balancer (API key, rate limit) to three forwarding API instances. A simulated sensor source, log-gen and log-sender, sends through the same load balancer. The API indexes through a HAProxy load balancer into a five-node Elasticsearch cluster: container logs into one index, sensor logs into another. Outside Docker, a terminal interface searches both through the API."
    what: "A scalable and secure logging infrastructure in Rust. It collects logs from syslog, stores them in an Elasticsearch cluster and makes them searchable through a terminal interface."
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
