from fastapi import FastAPI, Header
from datetime import datetime, timedelta
import random
import uvicorn

app = FastAPI(title="Mock Wazuh API")

ATTACK_SIGNATURES = {
    "T1110": ["Multiple authentication failures", "SSH brute force attempt detected", "Possible password attack"],
    "T1046": ["Nmap scan detected", "Port scanning activity", "Network reconnaissance detected"],
    "T1053": ["Suspicious cron job added", "Scheduled task created", "Crontab modification detected"],
    "T1070": ["Log file cleared", "Audit logs deleted", "System logs tampered"],
    "T1078": ["Login from unusual location", "Suspicious account activity", "Off-hours authentication detected"]
}

def generate_alert(technique_id, detected):
    if not detected:
        return []
    descriptions = ATTACK_SIGNATURES.get(technique_id, ["Suspicious activity detected"])
    return [{
        "_source": {
            "rule": {
                "description": random.choice(descriptions),
                "level": random.randint(7, 15),
                "mitre": {"technique": [technique_id]}
            },
            "agent": {"name": "debian-soc-agent"},
            "timestamp": datetime.utcnow().isoformat()
        }
    }]

@app.get("/")
def root():
    return {"message": "Mock Wazuh API running", "version": "4.7.0"}

@app.get("/security/user/authenticate")
def authenticate():
    return {"data": {"token": "mock-jwt-token-controlprobe"}}

@app.get("/alerts")
def get_alerts(technique_id: str = "T1110", detected: bool = True):
    alerts = generate_alert(technique_id, detected)
    return {
        "data": {
            "affected_items": alerts,
            "total_affected_items": len(alerts)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=55000)
