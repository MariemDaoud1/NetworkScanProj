# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pydantic import BaseModel
import nmap

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow only your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

scanned_hosts = set()

class ScanRequest(BaseModel):
    target: str
    ports: str
    scan_type: str

@app.get("/scan/{target}")
async def scan_target(target: str):
    try:
        nm = nmap.PortScanner()
        nm.scan(target, '1-100')
        scanned_hosts.add(target)
        if target not in nm.all_hosts():
            return {"error": "Could not scan the target. Check if it’s valid or reachable."}
        result = {"host": target, "status": nm[target].state(), "open_ports": []}
        for proto in nm[target].all_protocols():
            ports = nm[target][proto].keys()
            for port in ports:
                if nm[target][proto][port]['state'] == 'open':
                    result["open_ports"].append(port)
        return result
    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}

@app.get("/info/{target}")
async def get_target_info(target: str):
    try:
        nm = nmap.PortScanner()
        nm.scan(target, arguments="-sn")
        scanned_hosts.add(target)
        if target not in nm.all_hosts():
            return {"error": "Target not found or unreachable."}
        result = {"host": target, "status": nm[target].state(), "hostname": nm[target].hostname() or "Unknown"}
        return result
    except Exception as e:
        return {"error": f"Failed to get info: {str(e)}"}

@app.post("/custom-scan")
async def custom_scan(scan: ScanRequest):
    try:
        nm = nmap.PortScanner()
        nm.scan(scan.target, scan.ports, arguments=scan.scan_type)
        scanned_hosts.add(scan.target)
        if scan.target not in nm.all_hosts():
            return {"error": "Could not scan the target. Check if it’s valid or reachable."}
        result = {"host": scan.target, "status": nm[scan.target].state(), "open_ports": []}
        for proto in nm[scan.target].all_protocols():
            ports = nm[scan.target][proto].keys()
            for port in ports:
                if nm[scan.target][proto][port]['state'] == 'open':
                    result["open_ports"].append(port)
        return result
    except Exception as e:
        return {"error": f"Custom scan failed: {str(e)}"}

@app.get("/all-hosts")
async def list_scanned_hosts():
    if not scanned_hosts:
        return {"message": "No hosts have been scanned yet."}
    return {"scanned_hosts": list(scanned_hosts)}