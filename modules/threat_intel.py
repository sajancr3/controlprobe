import requests
import os
from dotenv import load_dotenv

load_dotenv()

class ThreatIntel:
    def __init__(self):
        self.api_key = os.getenv("ABUSEIPDB_API_KEY")
        self.base_url = "https://api.abuseipdb.com/api/v2"
        self.cache = {}

    def check_ip(self, ip):
        if ip in self.cache:
            return self.cache[ip]

        try:
            headers = {
                "Key": self.api_key,
                "Accept": "application/json"
            }
            params = {
                "ipAddress": ip,
                "maxAgeInDays": 90
            }
            res = requests.get(
                f"{self.base_url}/check",
                headers=headers,
                params=params,
                timeout=10
            )
            data = res.json().get("data", {})
            result = {
                "ip": ip,
                "abuse_score": data.get("abuseConfidenceScore", 0),
                "country": data.get("countryCode", "Unknown"),
                "isp": data.get("isp", "Unknown"),
                "domain": data.get("domain", "Unknown"),
                "total_reports": data.get("totalReports", 0),
                "last_reported": data.get("lastReportedAt", "Never"),
                "is_tor": data.get("isTor", False),
                "threat_level": self._threat_level(data.get("abuseConfidenceScore", 0))
            }
            self.cache[ip] = result
            return result
        except Exception as e:
            return {
                "ip": ip,
                "abuse_score": 0,
                "country": "Unknown",
                "isp": "Unknown",
                "domain": "Unknown",
                "total_reports": 0,
                "last_reported": "Never",
                "is_tor": False,
                "threat_level": "Unknown",
                "error": str(e)
            }

    def _threat_level(self, score):
        if score >= 80:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 20:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "CLEAN"

    def get_malicious_ips(self):
        """Returns a list of known malicious IPs for simulation"""
        return [
            "185.220.101.45",  # Known Tor exit node
            "89.248.167.131",  # Known scanner
            "45.153.160.2",    # Known brute force source
            "198.199.83.180",  # Known attacker
            "194.165.16.11"    # Known malicious
        ]
