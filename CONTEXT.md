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

---

## 6. 📚 Codebase Documentation (程式碼庫文檔)

**完整的程式碼庫文檔位於**: `docs/codebase/`

這個目錄包含了專案的完整技術文檔，涵蓋所有核心模組、應用結構和前端資源。

### 6.1. 文檔索引

| 文檔 | 路徑 | 描述 |
|------|------|------|
| **主索引** | `docs/codebase/README.md` | 文檔導航、快速開始、核心概念、API 速查 |
| **核心模組** | `docs/codebase/core_modules.md` | 19 個核心模組的詳細說明（服務層、資料存取、工具） |
| **應用結構** | `docs/codebase/app_structure.md` | Flask 應用、配置、Blueprint、API 端點 |
| **前端資源** | `docs/codebase/frontend_resources.md` | JavaScript、CSS、HTML 模板的功能說明 |

### 6.2. 文檔涵蓋範圍

- ✅ **74 個檔案**的完整分析（42 個 Python + 32 個前端）
- ✅ **2,500+ 行**詳細文檔
- ✅ **5 個 Mermaid 圖表**（架構圖、資料流程圖）
- ✅ **API 參考**、**最佳實踐**、**程式碼範例**

### 6.3. 如何使用文檔

**對於新功能開發**:
1. 先閱讀 `docs/codebase/README.md` 了解整體架構
2. 查看 `docs/codebase/core_modules.md` 了解可用的服務類別
3. 參考 `docs/codebase/app_structure.md` 了解如何添加新的 API 端點

**對於 Bug 修復**:
1. 在相關模組文檔中查找函數說明
2. 檢查資料流程圖理解資料如何流動
3. 參考最佳實踐避免常見錯誤

**對於程式碼審查**:
1. 對照文檔檢查是否遵循編碼規範
2. 驗證新程式碼是否符合架構設計
3. 確保文檔已同步更新

### 6.4. 文檔維護

- **更新頻率**: 當有重大架構變更或新增核心功能時
- **維護工具**: `scripts/tools/analyze_codebase.py` 可自動分析程式碼結構
- **責任**: 所有開發者在修改核心模組時應同步更新相關文檔

---

**💡 提示**: 在開始任何開發工作前，建議先閱讀 `docs/codebase/README.md` 以快速了解專案架構和可用資源。

