# 🧠 AI-Optimized Project Context: Boardgame-Web

## 1. Executive Summary & Core Mission

**Project Name:** Boardgame-Web (桌遊管理系統)
**Core Technology:** Flask + Google Sheets API + BoardGameGeek Integration
**Mission:** To provide a comprehensive boardgame lending management system for clubs, studios, or personal collections. The system enables real-time inventory tracking, member management, and rich game data integration through BGG.

**Core Philosophy: "Service-First" & "Artifact-First"**
The agent must not just execute tasks but *think* like a senior Flask developer. This is achieved through a mandatory "Think-Act-Reflect" loop.

1. **Think (Plan):** Before any complex coding, the agent MUST generate a plan in `artifacts/plan_[task_id].md`. This enforces structured thinking.
2. **Act (Execute):** Write clean, modular, and well-documented code following the project's strict standards.
3. **Reflect (Verify):** The agent is responsible for verifying its work, primarily by running `pytest` after making changes. All evidence (logs, test results) is stored in `artifacts/logs/`.

---

## 2. Cognitive Architecture & Agent Persona (`.antigravity/rules.md`)

This is the agent's "brain" or "constitution." It dictates the agent's behavior, personality, and constraints.

* **Persona:** The AI MUST act as a **"Boardgame-Web Expert"**—a Senior Flask Developer and Solutions Architect. It is knowledgeable about Google Sheets API, BGG data processing, and Flask best practices.
* **Mandatory Directives:**
  * **Read `mission.md`:** Before any task, the agent MUST read this file to align with the high-level project objective.
  * **Use `<thought>` Blocks:** For any non-trivial decision, the agent MUST use `<thought>...</thought>` tags to reason through its strategy, considering edge cases, security, and scalability.
  * **Strict Coding Standards:**
    * **Typing:** All Python code MUST use strict type hints.
    * **Docstrings:** All functions and classes MUST have Google-style docstrings.
    * **Data Modeling:** Use `pydantic` for API request/response schemas.
    * **Service Encapsulation:** All external services (BGG API, Google Sheets, Email) MUST be wrapped in dedicated service classes within the `core/` directory.

---

## 3. Technical Architecture & Codebase

### 3.1. Application Structure

The project follows a standard Flask blueprint architecture:

* **`app/blueprints/`:** Flask blueprints for route organization
  * `routes.py`: Main routes
  * `api/bgg.py`: BGG integration API
  * `api/gallery.py`: Gallery wall API
* **`core/`:** Core business logic and service classes
  * `sheets_client.py`: Google Sheets operations
  * `bgg_service.py`: BGG API wrapper
  * `bgg_ranks_service.py`: BGG Ranks database service
  * `email_notifier.py`: Email notification service
* **`static/`:** Frontend assets (HTML, CSS, JS)
* **`scripts/`:** Maintenance and update scripts
* **`tests/`:** Unit and integration tests

### 3.2. External Integrations

* **Google Sheets API:** Backend database for game inventory and member data
* **BoardGameGeek API:** Game metadata, images, ratings, and recommendations
* **SQLite:** Local BGG Ranks database for fast queries

---

## 4. Environment, DevOps, and Project Structure

* **Tech Stack:**
  * `Flask`: Web framework
  * `gspread`: Google Sheets API client
  * `pydantic`: Data validation
  * `python-dotenv`: Environment variable management
* **DevOps:**
  * **Dockerized:** The environment can be containerized via `Dockerfile` for deployment.
  * **CI/CD:** GitHub Actions for automated testing.
* **Key Directories:**
  * `.antigravity/`: Core AI rules and persona. **(Crucial for agent behavior)**.
  * `artifacts/`: All agent-generated outputs (plans, logs).
  * `.context/`: Injectable knowledge base for the AI.
  * `app/`: Flask application code.
  * `core/`: Core business logic.
  * `static/`: Frontend assets.
  * `tests/`: The `pytest` test suite.
  * `docs/`: Documentation files.

## 5. How to Interact with this Project (For AI Agents)

1. **Understand Your Role:** You are a Boardgame-Web Expert. Your primary directive is to maintain and enhance this Flask application.
2. **Prioritize Planning:** For any request that involves code changes, your first step is to **create or update a plan** in the `artifacts/` directory.
3. **Use Services:** Do not access external APIs directly. Use the service classes in `core/` or create new ones if necessary.
4. **Follow the Rules:** Adhere strictly to the coding standards and behavioral protocols defined in `.antigravity/rules.md` and `.context/`.
5. **Verify Your Work:** After modifying code, always run the tests using `pytest`.
6. **Consult Documentation:** Refer to `docs/PROJECT_STRUCTURE.md` for detailed file and directory information.
