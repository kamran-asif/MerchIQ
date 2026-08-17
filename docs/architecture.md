# Architecture Diagram

This file contains a standalone architecture diagram for MerchIQ and a short explanation.

```mermaid
flowchart TB
  subgraph FRONTEND
    B["Browser (React)"]
    UI["Vite Dev Server / UI"]
  end

  subgraph BACKEND
    API["FastAPI (app/main)"]
    SVC["Service Layer\n(pricing, forecasting, inventory, copilot)"]
    EVT["Event Bus / Workers"]
  end

  subgraph DATA
    DB["Postgres / SQL DB"]
    CACHE["Redis / Cache / Queue"]
  end

  EX["External APIs\n(weather, competitors, stores)"]

  B --> UI --> API
  API --> SVC
  SVC --> DB
  SVC --> CACHE
  API --> CACHE
  SVC --> EX
  SVC --> EVT
  EVT --> SVC

  classDef frontend fill:#8fd3ff,stroke:#222
  classDef backend fill:#ffdf7e,stroke:#222
  classDef data fill:#c8f7c5,stroke:#222

  class B,UI frontend
  class API,SVC,EVT backend
  class DB,CACHE data
```

Explanation

- The Browser loads the React app served by Vite (dev) or static assets (prod).
- The frontend makes HTTP calls to the FastAPI backend which routes requests under `backend/app/api/`.
- Business logic lives in the service layer (`backend/app/services/*`), which reads/writes from the primary database and uses Redis for caching and short-lived queues.
- An Event Bus and background workers handle asynchronous tasks (long-running forecasts, batch imports).
- External APIs provide supplementary data (weather, competitor pricing).

How to view

- GitHub will render the Mermaid diagram inside this Markdown file when viewed in the repo.
