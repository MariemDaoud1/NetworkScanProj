# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import nmap

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        print(f"Starting scan for {target}...")
        nm.scan(target, '1-100', arguments='-v -Pn')  # -Pn skips ping
        print(f"Nmap command: {nm.command_line()}")
        print(f"Scan results: {nm.all_hosts()}")
        if not nm.all_hosts():  # Check if any hosts were detected
            print(f"No hosts detected for {target}.")
            return {"error": "Could not scan the target. Check if it’s valid or reachable."}
        # Use the first detected host if target isn’t in results (e.g., IP vs hostname)
        host = target if target in nm.all_hosts() else nm.all_hosts()[0]
        result = {"host": target, "status": nm[host].state(), "open_ports": []}
        for proto in nm[host].all_protocols():
            ports = nm[host][proto].keys()
            for port in ports:
                if nm[host][proto][port]['state'] == 'open':
                    result["open_ports"].append(port)
        print(f"Scan completed: {result}")
        scanned_hosts.add(target)
        return result
    except Exception as e:
        print(f"Scan error: {str(e)}")
        return {"error": f"Something went wrong: {str(e)}"}

@app.get("/info/{target}")
async def get_target_info(target: str):
    try:
        nm = nmap.PortScanner()
        print(f"Starting info scan for {target}...")
        nm.scan(target, arguments="-sn -Pn")  # -Pn skips ping
        print(f"Info scan results: {nm.all_hosts()}")
        if not nm.all_hosts():
            print(f"No hosts detected for {target}.")
            return {"error": "Target not found or unreachable."}
        host = target if target in nm.all_hosts() else nm.all_hosts()[0]
        result = {"host": target, "status": nm[host].state(), "hostname": nm[host].hostname() or "Unknown"}
        print(f"Info completed: {result}")
        scanned_hosts.add(target)
        return result
    except Exception as e:
        print(f"Info error: {str(e)}")
        return {"error": f"Failed to get info: {str(e)}"}

@app.post("/custom-scan")
async def custom_scan(scan: ScanRequest):
    try:
        nm = nmap.PortScanner()
        print(f"Starting custom scan for {scan.target}...")
        nm.scan(scan.target, scan.ports, arguments=f"{scan.scan_type} -Pn")  # -Pn skips ping
        print(f"Custom scan results: {nm.all_hosts()}")
        if not nm.all_hosts():
            print(f"No hosts detected for {scan.target}.")
            return {"error": "Could not scan the target. Check if it’s valid or reachable."}
        host = scan.target if scan.target in nm.all_hosts() else nm.all_hosts()[0]
        result = {"host": scan.target, "status": nm[host].state(), "open_ports": []}
        for proto in nm[host].all_protocols():
            ports = nm[host][proto].keys()
            for port in ports:
                if nm[host][proto][port]['state'] == 'open':
                    result["open_ports"].append(port)
        print(f"Custom scan completed: {result}")
        scanned_hosts.add(scan.target)
        return result
    except Exception as e:
        print(f"Custom scan error: {str(e)}")
        return {"error": f"Custom scan failed: {str(e)}"}

@app.get("/all-hosts")
async def list_scanned_hosts():
    print(f"Scanned hosts: {scanned_hosts}")
    if not scanned_hosts:
        return {"message": "No hosts have been scanned yet."}
    return {"scanned_hosts": list(scanned_hosts)}