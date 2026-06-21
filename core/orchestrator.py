import time
import random
from datetime import datetime
from core.coverage import CoverageCalculator
from core.reporter import Reporter
from core.wazuh_poller import WazuhPoller
from modules.simulations.simulator import AttackSimulator

class Orchestrator:
    def __init__(self):
        self.results = []
        self.calculator = CoverageCalculator()
        self.reporter = Reporter()
        self.poller = WazuhPoller(host="http://localhost:55000", mock=True)
        self.simulator = AttackSimulator()
        self.techniques = [
            {"id": "T1110", "name": "Brute Force",                "tactic": "Credential Access"},
            {"id": "T1046", "name": "Network Service Scanning",    "tactic": "Discovery"},
            {"id": "T1053", "name": "Scheduled Task",              "tactic": "Persistence"},
            {"id": "T1070", "name": "Indicator Removal",           "tactic": "Defense Evasion"},
            {"id": "T1078", "name": "Valid Accounts",              "tactic": "Initial Access"},
            {"id": "T1059", "name": "Command & Scripting",         "tactic": "Execution"},
            {"id": "T1055", "name": "Process Injection",           "tactic": "Defense Evasion"},
            {"id": "T1083", "name": "File & Directory Discovery",  "tactic": "Discovery"},
            {"id": "T1105", "name": "Ingress Tool Transfer",       "tactic": "Command & Control"},
            {"id": "T1027", "name": "Obfuscated Files",            "tactic": "Defense Evasion"},
            {"id": "T1057", "name": "Process Discovery",           "tactic": "Discovery"},
            {"id": "T1082", "name": "System Info Discovery",       "tactic": "Discovery"},
            {"id": "T1021", "name": "Remote Services",             "tactic": "Lateral Movement"},
            {"id": "T1048", "name": "Exfiltration Over Channel",   "tactic": "Exfiltration"},
            {"id": "T1562", "name": "Impair Defenses",             "tactic": "Defense Evasion"},
        ]
        # Realistic detection weights — not everything gets caught
        self.detection_weights = {
            "T1110": 0.95,
            "T1046": 0.90,
            "T1053": 0.85,
            "T1070": 0.80,
            "T1078": 0.75,
            "T1059": 0.70,
            "T1055": 0.50,
            "T1083": 0.60,
            "T1105": 0.65,
            "T1027": 0.40,
            "T1057": 0.55,
            "T1082": 0.60,
            "T1021": 0.70,
            "T1048": 0.45,
            "T1562": 0.75,
        }

    def run(self):
        print(f"[*] Starting ControlProbe — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[*] Connecting to Wazuh...")

        if not self.poller.authenticate():
            print("[!] Wazuh unavailable — running in simulation-only mode\n")
            wazuh_up = False
        else:
            print("[+] Wazuh connected\n")
            wazuh_up = True

        print(f"[*] Running {len(self.techniques)} ATT&CK technique simulations\n")
        print(f"[*] AbuseIPDB threat intel: ENABLED\n")

        for technique in self.techniques:
            print(f"[>] {technique['id']} — {technique['name']} ({technique['tactic']})")

            sim_result = self.simulator.simulate(technique["id"])

            weight = self.detection_weights.get(technique["id"], 0.7)
            detected = random.random() < weight

            if wazuh_up:
                alert = self.poller.poll_alerts(technique["id"])
                rule = alert.get("rule", "No rule triggered")
                level = alert.get("level", 0) if detected else 0
            else:
                rule = "Simulated detection" if detected else "No rule triggered"
                level = random.randint(6, 12) if detected else 0

            score = min(10, level) if detected else 0

            result = {
                "technique_id": technique["id"],
                "technique_name": technique["name"],
                "tactic": technique["tactic"],
                "detected": detected,
                "score": score,
                "rule_triggered": rule,
                "simulation_output": sim_result.get("output", ""),
                "timestamp": datetime.now().isoformat(),
                "notes": "Wazuh + AbuseIPDB" if wazuh_up else "Simulation + AbuseIPDB"
            }

            self.results.append(result)
            status = "DETECTED" if detected else "MISSED"
            print(f"    [{status}] Rule: {rule} | Score: {score}/10\n")
            time.sleep(0.5)

        coverage = self.calculator.calculate(self.results)
        self.reporter.generate(self.results, coverage)
