# ControlProbe — Adaptive Security Control Validator

> Automatically tests whether your security controls detect real ATT&CK techniques — then scores, grades, and visualizes your coverage gaps.

![Python](https://img.shields.io/badge/Python-3.9-blue) ![Docker](https://img.shields.io/badge/Docker-Compose-blue) ![MITRE](https://img.shields.io/badge/MITRE-ATT%26CK-red) ![AbuseIPDB](https://img.shields.io/badge/ThreatIntel-AbuseIPDB-orange)

---

## What It Does

Most security teams *assume* their controls work. ControlProbe *proves* it.

ControlProbe simulates 15 real ATT&CK techniques across 9 tactics, polls a SIEM (Wazuh) for alert responses, enriches attacker IPs with live AbuseIPDB threat intelligence, and produces a scored coverage report with gap analysis — all visualized in a live dashboard.

---

## Architecture
---

## ATT&CK Techniques Covered

| ID | Technique | Tactic |
|---|---|---|
| T1110 | Brute Force | Credential Access |
| T1046 | Network Service Scanning | Discovery |
| T1053 | Scheduled Task | Persistence |
| T1070 | Indicator Removal | Defense Evasion |
| T1078 | Valid Accounts | Initial Access |
| T1059 | Command & Scripting | Execution |
| T1055 | Process Injection | Defense Evasion |
| T1083 | File & Directory Discovery | Discovery |
| T1105 | Ingress Tool Transfer | Command & Control |
| T1027 | Obfuscated Files | Defense Evasion |
| T1057 | Process Discovery | Discovery |
| T1082 | System Info Discovery | Discovery |
| T1021 | Remote Services | Lateral Movement |
| T1048 | Exfiltration Over Channel | Exfiltration |
| T1562 | Impair Defenses | Defense Evasion |

---

## Features

- Real ATT&CK technique simulations — not synthetic data
- Wazuh SIEM integration with live alert polling
- AbuseIPDB threat intelligence enrichment on attacker IPs
- Realistic detection rates — weighted per technique difficulty
- Coverage scoring with A-D grading
- Gap analysis — identifies exactly what your controls miss
- Historical JSON reports — track improvement over time
- Live web dashboard with radar chart and tactic breakdown
- Fully Dockerized — runs with one command

---

## Quick Start

```bash
git clone https://github.com/sajancr3/controlprobe.git
cd controlprobe
cp .env.example .env
# Add your AbuseIPDB API key to .env
docker compose up
```

Open dashboard: http://localhost:8080

Run a scan:
```bash
docker compose run runner
```

---

## Tech Stack

- Python 3.9
- FastAPI + Uvicorn
- Docker + Docker Compose
- Wazuh REST API
- AbuseIPDB API
- Chart.js
- MITRE ATT&CK Framework

---

## Environment Variables
ABUSEIPDB_API_KEY=your_key_here

WAZUH_HOST=http://localhost:55000

WAZUH_MOCK=true

Set `WAZUH_MOCK=false` and point `WAZUH_HOST` to a real Wazuh instance to use live SIEM data.

---

## Built On

Debian ARM64 — part of a cybersecurity portfolio demonstrating detection engineering, SIEM integration, and threat intelligence operationalization.

