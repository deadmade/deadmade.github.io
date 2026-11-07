# Validation: IsoPrüfi drawing (study-06-c/work.html, lines 187-222)

Source checked: https://github.com/deadmade/IsoPruefi, default branch `main` (full clone, 752 commits), plus
https://isopruefi.manuelschuelein.de/documentation/05_context_and_scope/. Paths below are relative to the repository root.

| # | claim | verdict | how known | evidence, or what is the case instead |
|---|-------|---------|-----------|----------------------------------------|
| I1 | Arduinos measure indoor temperature; two, north and south, one sensor each | CONFIRMED | verified | `README.md:8` "collected from the north and south sides of the building"; `README.md:14` "2 Arduinos with one temperature sensor each, RTC modules and SD card modules". One firmware with a compile-time ID switch: `isopruefi-arduino/src/core.cpp:30-33` (`Sensor_One` / `Sensor_Two`). Seed data maps them to North/South: `isopruefi-backend/Database/EntityFramework/ApplicationDbContext.cs:49,55`. Board MKR WiFi 1010, sensor ADT7410: `isopruefi-arduino/platformio.ini:14-20`. |
| I2 | Outdoor temperature comes from a weather API, not the Arduinos | CONFIRMED | verified | Two services: Open-Meteo (primary) and Bright Sky (fallback). `isopruefi-backend/Get-weatherData-worker/Worker.cs:59-63,95,113`; URLs in `Get-weatherData-worker/appsettings.Development.json:16-17` (`api.open-meteo.com`, `api.brightsky.dev`). Arduinos only publish indoor sensor readings (`isopruefi-arduino/src/mqtt.cpp:175-230`). |
| I3 | Arduinos send measurements to the ASP.NET Core service (one direct arrow) | CONTRADICTED | verified | Not direct. Arduino publishes MQTT (QoS 1) over Wi-Fi to an external broker `aicon.dhbw-heidenheim.de:1883` (`isopruefi-arduino/src/network.cpp:13-14,61`; `mqtt.cpp:195`). A separate .NET worker, `MQTT-Receiver-Worker`, subscribes with shared subscriptions (`MQTT-Receiver-Worker/MQTT/Receiver.cs:84-90`) and writes to InfluxDB (`MQTT/Connection.cs:249,300`). When offline, readings are buffered as CSV on an SD card and re-sent later on a `/recovered` topic (`mqtt.cpp:215-217,333`). The REST API never receives sensor data. Docs agree: "Arduino → MQTT Broker → MQTT Receiver Worker" (docs site, context page). |
| I4 | The ASP.NET Core service fetches outdoor temperature from the weather API (pull) | PARTLY | verified | Pull is correct: HTTP GET every ~10 s, `Get-weatherData-worker/Worker.cs:169,216,131`. But the caller is a separate worker process (`Get-weatherData-worker`, own container), not the REST API service the drawing shows. The REST API itself calls only Nominatim for geocoding postal codes (`Rest-API/Services/Temp/TempService.cs:55,177`). |
| I5 | Service stores data in PostgreSQL | CONFIRMED | verified | EF Core + Npgsql: `Rest-API/Program.cs:61-63`; `Database/Database.csproj:21`. The weather worker and MQTT worker also read PostgreSQL (`Database/Repository/CoordinateRepo/CoordinateRepo.cs:85-91`, `MQTT-Receiver-Worker/MQTT/Receiver.cs:63-65`). |
| I6 | Service stores data in InfluxDB | PARTLY | verified | InfluxDB 3 is used (`Database/Database.csproj:12`, `docker-compose.yml` service `influxdb3`). But the writes come from the two workers (`InfluxRepo.cs:45-95` called from `MQTT/Connection.cs:249,300` and `Get-weatherData-worker/Worker.cs:102,119`); the REST API only reads InfluxDB (`Rest-API/Controllers/TemperatureController.cs:251,305`). |
| I7 | What is in PostgreSQL vs InfluxDB | CONFIRMED (stated here) | verified | PostgreSQL: ASP.NET Identity users/roles, refresh tokens, MQTT topic/sensor settings (name, North/South location), postal-code-to-coordinate mappings with worker locks (`Database/EntityFramework/ApplicationDbContext.cs:10,20,25,30`). InfluxDB: measurements `temperature` (indoor, per sensor), `outside_temperature` (per place and source, °C and °F), `uptime` (sensor heartbeats) (`Database/Repository/InfluxRepo/Influx/InfluxRepo.cs:51,65,91`). |
| I8 | Service serves a React front end; React reads data from the service | PARTLY | verified | Data flow is right: the React app calls the REST API via generated clients at `/backend` (`isopruefi-frontend/src/api/clients.ts:42-57`, `public/config.json`, `src/components/Weather.tsx:86`). "Serves" is wrong: the built React app is served by nginx in its own container (`isopruefi-frontend/Dockerfile:30-42`), routed by Traefik (`isopruefi-docker-live/docker-compose.yml:196,232`); the API has no static-file/SPA hosting. The drawing's arrow direction (service → React) matches response data flow, but requests start in the browser. |
| I9 | Backend ASP.NET Core (.NET), front end React | CONFIRMED | verified | `Rest-API/Rest-API.csproj:1` `Microsoft.NET.Sdk.Web`, net9.0; workers also use `WebApplication.CreateBuilder` (`MQTT-Receiver-Worker/Program.cs:27`, `Get-weatherData-worker/Program.cs:27`). React 19 + Vite + TypeScript, charts with Recharts (`isopruefi-frontend/package.json:15,18,32,34`). |
| I10 | Nothing between Arduinos and service, nor between service and databases | CONTRADICTED | verified | Between Arduinos and backend: an external MQTT broker (`network.cpp:13`) and a dedicated MQTT receiver worker. Between browser and API: Traefik reverse proxy/load balancer with two replicas of each app container (`isopruefi-docker-live/docker-compose.yml:187-337`). Between services and InfluxDB: a write buffer in memory cache plus a retry service when InfluxDB is down (`Database/Repository/InfluxRepo/InfluxCache/CachedInfluxRepo.cs:11`, `MQTT-Receiver-Worker/Program.cs:32,52`). Nothing sits between services and PostgreSQL. |
| I11 | Main technologies ASP.NET Core, React, PostgreSQL, InfluxDB; anything major missing | PARTLY | verified | All four are right. Missing and major for this project: MQTT (the sensor transport, MQTTnet in `MQTT-Receiver-Worker.csproj:21`), Arduino/C++ firmware (PlatformIO), Docker Compose + Traefik. Secondary: Grafana/Loki/Prometheus/Alloy monitoring (`docker-compose.yml`). |
| I12 | Team build; number of distinct commit authors | CONFIRMED | verified | 4 distinct human authors on `main` (6 author names, two of them aliases of the same GitHub accounts), plus dependabot. `git shortlog -sne HEAD`. |
| T1 | "Analyze building insulation" | CONFIRMED | verified | `README.md:7` "test the effectiveness of building insulation". |
| T2 | "by comparing indoor temperature ... with outdoor temperature" | CONFIRMED | verified | `README.md:7-8` "compares the interior and exterior temperature data"; API combines both: `TemperatureController.cs:51,65-76`. |
| T3 | "measured by Arduino devices on the north and south sides of the building" | CONFIRMED | verified | See I1. |
| T4 | "outdoor temperature from a weather API" | CONFIRMED | verified | See I2 (Open-Meteo, Bright Sky fallback). Singular "a weather API" is a simplification, not false. |

## Drawing shows beyond the claims list, false or misleading

- One "ASP.NET Core" box: the backend is three separately deployed .NET services (REST API, MQTT receiver worker,
  weather worker), each run as two replicas in production (`isopruefi-docker-live/docker-compose.yml:227-337`). Arrows
  into the box from Arduinos and weather API end at the workers, not at the API that React talks to.
- Both database arrows point from the service into the databases. For the REST API, InfluxDB is read only, and the
  workers also read PostgreSQL (topics, coordinates). The arrows are acceptable as "stores data" only if the box means
  "the backend as a whole".
- The SVG `<title>` says the service "serves a React front end"; nginx serves it (see I8).

## Components or data paths the drawing leaves out (top 3)

1. MQTT broker (external, DHBW host) and the MQTT receiver worker: the real ingestion path for indoor data.
2. Offline resilience on the Arduino: RTC timestamps plus SD-card CSV buffering and recovery publishing; the README
   names reliability under partial failure as a design goal (`README.md:9-10`).
3. Traefik reverse proxy and load balancing over duplicated containers (and the Grafana/Loki/Prometheus monitoring stack).

## Not checked

- Hardware deployment (whether two physical Arduinos were actually installed on north/south walls) beyond README and
  seed data.
- Only one docs page (context and scope) was fetched; it agrees with the code on all points checked.
- Rendered page at 127.0.0.1:8766 not opened; the SVG source was read instead.
- Nothing was built or run.
