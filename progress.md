# Project Progress Log

This project was developed as part of a personal 29-day challenge, focused on building a fully functional and monitored infrastructure using tools like Flask, PostgreSQL, Docker, Prometheus, Grafana, AWS EC2, GitHub Actions, and more.

Below is a day-by-day summary of the development progress:

| Day   | Progress Summary                                                                                                                    |
|-------|-------------------------------------------------------------------------------------------------------------------------------------|
| 1     | Base setup: Flask API, PostgreSQL integration, Prometheus metrics, Grafana dashboard                                                |
| 2     | Simulated infrastructure servers and metrics storage using PostgreSQL                                                               |
| 3     | Implemented logging system and `/health` endpoint                                                                                   |
| 4     | Added Prometheus metrics for request tracking and server monitoring                                                                 |
| 5     | Dockerized the application; created Dockerfile and docker-compose with DB                                                           |
| 6     | Full CRUD implementation for servers with PostgreSQL integration                                                                    |
| 7     | Exposed simulated CPU, memory, and state metrics for DB servers                                                                     |
| 8–10  | Integrated advanced server metrics, exposed `/metrics` endpoint, added Grafana dashboards, and enhanced logging and API validation  |
| 11–13 | Added CI pipeline using GitHub Actions and pytest; introduced REBOOTING state; persisted server states in PostgreSQL                |
| 14–15 | Created `/lifecycle` endpoint; connected backend to PostgreSQL; added initial app setup                                             |
| 16–17 | Completed AWS account setup, installed/configured AWS CLI, created and connected to EC2 instance |
| 18    | Fixed CI issues using SQLite for test environment (`FLASK_ENV=testing`) |
| 19    | Added GitHub Action to build and push Docker image to DockerHub |
| 20    | Updated README with project notes and additional improvements |
| 21    | Implemented server lifecycle simulation, improved error handling, and added unit tests |
| 22    | Dockerized the full stack (App, DB, Prometheus, Grafana) and fixed configuration issues |
| 23    | Launched and configured EC2 instance for AWS deployment |
| 24    | Set up backend services (PostgreSQL, Prometheus, Grafana) using Docker |
| 25    | Made minor improvements to Docker configuration and Prometheus setup |
| 26    | Set up local Prometheus and Grafana instances; validated API endpoints |
| 27    | Finalized cloud-based Prometheus/Grafana setup and validated remote API |
| 28    | Added auto-deploy to EC2 using Docker Compose and AWS CLI commands |
| 29    | Final project adjustments, added flowchart diagram, and completed README documentation |
