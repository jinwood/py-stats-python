from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
import os
from typing import Dict, List, Optional, Union

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def get_cpu_temp() -> Optional[float]:
    """Get CPU temperature"""
    try:
        temp = os.popen("vcgencmd measure_temp").readline()
        return float(temp.replace("temp=", "").replace("'C\n", ""))
    except (ValueError, OSError) as e:
        print(f"Error reading CPU temperature: {e}")
        return None


def get_system_info() -> Dict[str, Dict[str, Union[float, int, None]]]:
    """Get comprehensive system information"""
    return {
        "cpu": {
            "usage_percent": psutil.cpu_percent(interval=1),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "temperature": get_cpu_temp(),
            "cores": psutil.cpu_count(),
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent_used": psutil.virtual_memory().percent,
        },
        "disk": {
            "total": psutil.disk_usage("/").total,
            "used": psutil.disk_usage("/").used,
            "free": psutil.disk_usage("/").free,
            "percent_used": psutil.disk_usage("/").percent,
        },
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv,
        },
    }


def get_running_processes() -> List[Dict[str, Union[int, str, float]]]:
    """Get list of running processes"""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error accessing process: {e}")
            continue
    return sorted(processes, key=lambda x: x.get("cpu_percent", 0), reverse=True)[:10]


@app.get("/api/system")
async def system():
    return get_system_info()


@app.get("/api/processes")
async def processes():
    return get_running_processes()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
