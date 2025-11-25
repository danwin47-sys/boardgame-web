# Boardgame Web App

This repository contains a simple web application for managing board games.

## Contents
- **index.html** – Front‑end UI (HTML, CSS, JavaScript) that runs on GitHub Pages.
- **flask_app.py** – Flask API (runs on Render or any Docker host).
- **boardgame_system.py** – Core logic for board‑game data and member lookup.
- **Dockerfile** – Docker image definition for the Flask service.
- **requirements.txt** – Python dependencies (`flask` and `flask‑cors`).
- **README.md** – This file.

## How it works
1. **Front‑end** is served via GitHub Pages at `https://danwin47-sys.github.io/boardgame-web/`.
2. The front‑end talks to the back‑end API (hosted on Render) using the `apiBase` variable defined in `index.html`.
3. The back‑end reads `sheet1.json` (board‑game data) and `sheet3.json` (member data) from the repository.
4. Borrow/return actions update the JSON files and refresh the UI.

## Deployment steps (already done)
1. Push all files to the GitHub repo `danwin47-sys/boardgame-web`.
2. Enable GitHub Pages (Settings → Pages → Source: `main` → `/`).
3. Create a free Render Web Service pointing to this repo (Docker environment).
4. Update `apiBase` in `index.html` to the Render URL.

## Local testing
```bash
# Run the Flask API locally
python flask_app.py
# Open index.html in a browser (file://) – it will call the local API at http://localhost:5000/api
```

Feel free to fork, modify, or extend this project!
