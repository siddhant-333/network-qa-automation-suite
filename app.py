from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Network Device Status Monitor")

# Simulated in-memory list of network devices
devices = [
    {"id": "dev-1", "name": "core-router-ott-01", "type": "router", "status": "Online", "latency_ms": 12},
    {"id": "dev-2", "name": "agg-switch-ott-02", "type": "switch", "status": "Degraded", "latency_ms": 85},
    {"id": "dev-3", "name": "edge-fw-ott-03", "type": "firewall", "status": "Offline", "latency_ms": 0},
]

class StatusUpdate(BaseModel):
    status: str

VALID_STATUSES = {"Online", "Degraded", "Offline"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "network-monitor"}

@app.get("/devices")
def list_devices(status: Optional[str] = None, format: str = "json"):
    filtered = devices
    if status and status != "All":
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid status filter")
        filtered = [d for d in devices if d["status"] == status]

    if format.lower() == "xml":
        items_xml = "".join(
            f"<device><id>{d['id']}</id><name>{d['name']}</name>"
            f"<type>{d['type']}</type><status>{d['status']}</status>"
            f"<latency_ms>{d['latency_ms']}</latency_ms></device>"
            for d in filtered
        )
        return Response(content=f"<devices>{items_xml}</devices>", media_type="application/xml")

    return {"count": len(filtered), "devices": filtered}

@app.get("/devices/{device_id}")
def get_device(device_id: str):
    for d in devices:
        if d["id"] == device_id:
            return d
    raise HTTPException(status_code=404, detail="Device not found")

@app.patch("/devices/{device_id}/status")
def update_device_status(device_id: str, payload: StatusUpdate):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Status must be Online, Degraded, or Offline")
    for d in devices:
        if d["id"] == device_id:
            d["status"] = payload.status
            d["latency_ms"] = 0 if payload.status == "Offline" else (85 if payload.status == "Degraded" else 14)
            return d
    raise HTTPException(status_code=404, detail="Device not found")

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Network Device Status Monitor</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
            h1 { color: #14345c; }
            .controls { margin-bottom: 16px; }
            select, button { padding: 6px 10px; font-size: 14px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
            th { background-color: #f4f6f9; }
            .Online { color: green; font-weight: bold; }
            .Degraded { color: #d97706; font-weight: bold; }
            .Offline { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Network Device Status Monitor</h1>
        <div class="controls">
            <label for="statusFilter">Filter by Status: </label>
            <select id="statusFilter" onchange="loadDevices()">
                <option value="All">All</option>
                <option value="Online">Online</option>
                <option value="Degraded">Degraded</option>
                <option value="Offline">Offline</option>
            </select>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Device Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Latency (ms)</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="deviceTableBody"></tbody>
        </table>

        <script>
            async function loadDevices() {
                const filter = document.getElementById("statusFilter").value;
                const res = await fetch(`/devices?status=${filter}`);
                const data = await res.json();
                const tbody = document.getElementById("deviceTableBody");
                tbody.innerHTML = "";
                data.devices.forEach(d => {
                    const row = `<tr>
                        <td>${d.id}</td>
                        <td>${d.name}</td>
                        <td>${d.type}</td>
                        <td class="${d.status}" data-testid="status-${d.id}">${d.status}</td>
                        <td>${d.latency_ms}</td>
                        <td>
                            <button onclick="setOnline('${d.id}')" data-testid="btn-online-${d.id}">Set Online</button>
                        </td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            }

            async function setOnline(id) {
                await fetch(`/devices/${id}/status`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status: "Online" })
                });
                loadDevices();
            }

            loadDevices();
        </script>
    </body>
    </html>
    """