 Network QA Automation Suite

A lightweight mock network device status monitoring web service built with Python and FastAPI, paired with automated API testing using Postman/Newman and UI testing with Playwright.

Project Structure

- `app.py` — FastAPI backend and HTML dashboard for viewing and updating network device statuses (`Online` / `Offline`).
- `postman/network_api_collection.json` — Postman test collection covering health checks, JSON/XML device queries, 404 error handling, and status updates.

 Prerequisites
- Python 3.10+
- Node.js & npm (for Newman CLI test runs)
- Postman Desktop App

How to Run Locally

1. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn
