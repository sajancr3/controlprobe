import requests
import time

class WazuhPoller:
    def __init__(self, host="http://localhost:55000", mock=True):
        self.host = host
        self.mock = mock
        self.token = None

    def authenticate(self):
        try:
            res = requests.get(f"{self.host}/security/user/authenticate", timeout=5)
            self.token = res.json()["data"]["token"]
            return True
        except Exception as e:
            print(f"    [!] Wazuh auth failed: {e}")
            return False

    def poll_alerts(self, technique_id, wait_seconds=3):
        print(f"    [~] Polling Wazuh for {technique_id} alerts...")
        time.sleep(wait_seconds)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.get(
                f"{self.host}/alerts",
                params={"technique_id": technique_id, "detected": True},
                headers=headers,
                timeout=5
            )
            data = res.json()
            alerts = data.get("data", {}).get("affected_items", [])
            if alerts:
                alert = alerts[0]["_source"]
                return {
                    "detected": True,
                    "rule": alert["rule"]["description"],
                    "level": alert["rule"]["level"],
                    "agent": alert["agent"]["name"],
                    "timestamp": alert["timestamp"]
                }
            return {"detected": False, "rule": None, "level": 0, "agent": None, "timestamp": None}
        except Exception as e:
            print(f"    [!] Poll error: {e}")
            return {"detected": False, "rule": None, "level": 0, "agent": None, "timestamp": None}
