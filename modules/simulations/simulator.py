import subprocess
import os
import tempfile
from datetime import datetime
from modules.threat_intel import ThreatIntel

class AttackSimulator:
    def __init__(self):
        self.ti = ThreatIntel()
        self.malicious_ips = self.ti.get_malicious_ips()

    def simulate(self, technique_id):
        simulations = {
            "T1110": self.simulate_brute_force,
            "T1046": self.simulate_port_scan,
            "T1053": self.simulate_cron_persistence,
            "T1070": self.simulate_log_clearing,
            "T1078": self.simulate_suspicious_login,
            "T1059": self.simulate_command_execution,
            "T1055": self.simulate_process_injection,
            "T1083": self.simulate_file_discovery,
            "T1105": self.simulate_ingress_transfer,
            "T1027": self.simulate_obfuscation,
            "T1057": self.simulate_process_discovery,
            "T1082": self.simulate_system_info,
            "T1021": self.simulate_remote_services,
            "T1048": self.simulate_exfiltration,
            "T1562": self.simulate_defense_impairment
        }
        fn = simulations.get(technique_id)
        if fn:
            return fn()
        return {"success": False, "output": "Unknown technique"}

    def _enrich_ip(self, ip):
        intel = self.ti.check_ip(ip)
        return (
            f"IP: {ip} | Score: {intel['abuse_score']}/100 | "
            f"Country: {intel['country']} | ISP: {intel['isp']} | "
            f"Threat: {intel['threat_level']} | Reports: {intel['total_reports']}"
        )

    def simulate_brute_force(self):
        print("    [SIM] Simulating SSH brute force (T1110)...")
        ip = self.malicious_ips[0]
        intel = self._enrich_ip(ip)
        output = f"5 failed SSH logins from attacker\n{intel}"
        self._write_auth_log(ip)
        return {"success": True, "output": output, "technique": "T1110"}

    def simulate_port_scan(self):
        print("    [SIM] Simulating network port scan (T1046)...")
        ip = self.malicious_ips[1]
        intel = self._enrich_ip(ip)
        output = f"Port scan on 22,80,443,3306 from attacker\n{intel}"
        return {"success": True, "output": output, "technique": "T1046"}

    def simulate_cron_persistence(self):
        print("    [SIM] Simulating cron persistence (T1053)...")
        cron = "*/5 * * * * /tmp/.hidden_payload.sh"
        tmp = tempfile.mktemp()
        with open(tmp, "w") as f:
            f.write(f"# ControlProbe simulation\n{cron}\n")
        os.remove(tmp)
        return {"success": True, "output": f"Malicious cron entry simulated:\n{cron}", "technique": "T1053"}

    def simulate_log_clearing(self):
        print("    [SIM] Simulating log clearing (T1070)...")
        tmp = tempfile.mktemp(suffix=".log")
        with open(tmp, "w") as f:
            f.write("log entry\n" * 10)
        before = os.path.getsize(tmp)
        open(tmp, "w").close()
        os.remove(tmp)
        return {"success": True, "output": f"Log truncated: {before} bytes → 0 bytes", "technique": "T1070"}

    def simulate_suspicious_login(self):
        print("    [SIM] Simulating suspicious login (T1078)...")
        ip = self.malicious_ips[2]
        intel = self._enrich_ip(ip)
        hour = datetime.now().hour
        timing = "OFF-HOURS" if hour < 6 or hour > 22 else "BUSINESS HOURS"
        output = f"Login at {datetime.now().strftime('%H:%M:%S')} ({timing})\n{intel}"
        return {"success": True, "output": output, "technique": "T1078"}

    def simulate_command_execution(self):
        print("    [SIM] Simulating command execution (T1059)...")
        cmds = ["whoami", "id", "uname -a"]
        results = []
        for cmd in cmds:
            try:
                out = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
                results.append(f"{cmd}: {out.stdout.strip()}")
            except Exception:
                results.append(f"{cmd}: simulated")
        return {"success": True, "output": "\n".join(results), "technique": "T1059"}

    def simulate_process_injection(self):
        print("    [SIM] Simulating process injection (T1055)...")
        try:
            procs = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            target = procs.stdout.split("\n")[1].split()[1] if procs.stdout else "1234"
            output = f"Injection attempt simulated on PID {target}"
        except Exception:
            output = "Process injection simulated on PID 1234"
        return {"success": True, "output": output, "technique": "T1055"}

    def simulate_file_discovery(self):
        print("    [SIM] Simulating file discovery (T1083)...")
        sensitive = ["/etc/passwd", "/etc/shadow", "/etc/hosts", "~/.ssh/"]
        found = [f for f in sensitive if os.path.exists(f.replace("~", os.path.expanduser("~")))]
        output = f"Sensitive files discovered:\n" + "\n".join(found)
        return {"success": True, "output": output, "technique": "T1083"}

    def simulate_ingress_transfer(self):
        print("    [SIM] Simulating ingress tool transfer (T1105)...")
        ip = self.malicious_ips[3]
        intel = self._enrich_ip(ip)
        output = f"Tool download simulated from C2\n{intel}"
        return {"success": True, "output": output, "technique": "T1105"}

    def simulate_obfuscation(self):
        print("    [SIM] Simulating obfuscated payload (T1027)...")
        import base64
        payload = base64.b64encode(b"malicious_command --execute").decode()
        output = f"Base64 obfuscated payload detected:\n{payload}"
        return {"success": True, "output": output, "technique": "T1027"}

    def simulate_process_discovery(self):
        print("    [SIM] Simulating process discovery (T1057)...")
        try:
            out = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            count = len(out.stdout.split("\n"))
            output = f"Process enumeration: {count} processes discovered"
        except Exception:
            output = "Process enumeration simulated: 87 processes discovered"
        return {"success": True, "output": output, "technique": "T1057"}

    def simulate_system_info(self):
        print("    [SIM] Simulating system info collection (T1082)...")
        try:
            uname = subprocess.run(["uname", "-a"], capture_output=True, text=True)
            output = f"System info collected:\n{uname.stdout.strip()}"
        except Exception:
            output = "System info collection simulated"
        return {"success": True, "output": output, "technique": "T1082"}

    def simulate_remote_services(self):
        print("    [SIM] Simulating remote service abuse (T1021)...")
        ip = self.malicious_ips[4]
        intel = self._enrich_ip(ip)
        output = f"RDP/SSH lateral movement simulated\n{intel}"
        return {"success": True, "output": output, "technique": "T1021"}

    def simulate_exfiltration(self):
        print("    [SIM] Simulating data exfiltration (T1048)...")
        ip = self.malicious_ips[0]
        intel = self._enrich_ip(ip)
        output = f"DNS exfiltration simulated to C2\n{intel}"
        return {"success": True, "output": output, "technique": "T1048"}

    def simulate_defense_impairment(self):
        print("    [SIM] Simulating defense impairment (T1562)...")
        output = "Firewall rule deletion simulated\nAV process termination simulated"
        return {"success": True, "output": output, "technique": "T1562"}

    def _write_auth_log(self, ip):
        try:
            with open("/tmp/controlprobe_auth.log", "a") as f:
                for i in range(5):
                    f.write(f"{datetime.now().isoformat()} Failed login from {ip}\n")
        except Exception:
            pass
