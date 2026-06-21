from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
import os
import glob

app = FastAPI(title="ControlProbe Dashboard")

def get_latest_report():
    reports = glob.glob("reports/*.json")
    if not reports:
        return None
    latest = max(reports, key=os.path.getctime)
    with open(latest) as f:
        return json.load(f)

@app.get("/", response_class=HTMLResponse)
def dashboard():
    report = get_latest_report()
    if not report:
        return "<h2>No reports yet. Run python3 main.py first.</h2>"

    summary = report["summary"]
    tactics = report["tactic_coverage"]
    gaps = report["gaps"]
    results = report["results"]

    tactic_rows = ""
    for tactic, pct in tactics.items():
        color = "#00ff88" if pct == 100 else "#ffb347" if pct >= 50 else "#ff4d4d"
        tactic_rows += f"""
        <div class="tactic-row">
            <span class="tactic-name">{tactic}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%;background:{color}"></div>
            </div>
            <span class="tactic-pct" style="color:{color}">{pct}%</span>
        </div>"""

    result_rows = ""
    for r in results:
        detected = r["detected"]
        badge_class = "badge-detected" if detected else "badge-missed"
        badge_text = "DETECTED" if detected else "MISSED"
        score_color = "#00ff88" if r["score"] >= 7 else "#ffb347" if r["score"] >= 5 else "#ff4d4d"
        result_rows += f"""
        <tr>
            <td><span class="technique-id">{r['technique_id']}</span></td>
            <td class="technique-name">{r['technique_name']}</td>
            <td><span class="tactic-tag">{r['tactic']}</span></td>
            <td><span class="badge {badge_class}">{badge_text}</span></td>
            <td><span style="color:{score_color};font-weight:700">{r['score']}</span><span class="score-max">/10</span></td>
            <td class="timestamp">{r['timestamp'][11:19]}</td>
        </tr>"""

    gap_items = ""
    if gaps:
        for g in gaps:
            gap_items += f'<div class="gap-item">⚠ {g}</div>'
    else:
        gap_items = '<div class="no-gap">✓ No coverage gaps detected</div>'

    grade = summary['grade'].split('—')[0].strip()
    pct = summary['coverage_percentage']
    grade_color = "#00ff88" if pct >= 90 else "#ffb347" if pct >= 70 else "#ff4d4d"

    tactic_labels = list(tactics.keys())
    tactic_values = list(tactics.values())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ControlProbe</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

        * {{ margin:0; padding:0; box-sizing:border-box; }}

        body {{
            background: #060b14;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }}

        .bg-grid {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }}

        .container {{
            position: relative;
            z-index: 1;
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px 24px;
        }}

        /* HEADER */
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 40px;
            padding-bottom: 24px;
            border-bottom: 1px solid rgba(0,255,136,0.1);
        }}
        .logo {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .logo-icon {{
            width: 44px; height: 44px;
            background: linear-gradient(135deg, #00ff88, #00b4d8);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
        }}
        .logo-text h1 {{
            font-size: 22px;
            font-weight: 700;
            color: #fff;
            letter-spacing: -0.5px;
        }}
        .logo-text span {{
            font-size: 12px;
            color: #64748b;
            font-family: 'JetBrains Mono', monospace;
        }}
        .header-meta {{
            text-align: right;
        }}
        .report-id {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #00ff88;
            background: rgba(0,255,136,0.08);
            padding: 4px 10px;
            border-radius: 20px;
            border: 1px solid rgba(0,255,136,0.2);
        }}
        .report-time {{
            font-size: 11px;
            color: #475569;
            margin-top: 6px;
        }}

        /* SCORE HERO */
        .score-hero {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}
        .score-card {{
            background: linear-gradient(135deg, rgba(0,255,136,0.05), rgba(0,180,216,0.05));
            border: 1px solid rgba(0,255,136,0.15);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        .score-card::before {{
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(0,255,136,0.05) 0%, transparent 60%);
            pointer-events: none;
        }}
        .score-number {{
            font-size: 72px;
            font-weight: 800;
            line-height: 1;
            color: {grade_color};
            font-family: 'JetBrains Mono', monospace;
            text-shadow: 0 0 40px {grade_color}44;
        }}
        .score-label {{
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 8px;
        }}
        .grade-badge {{
            display: inline-block;
            margin-top: 16px;
            padding: 6px 16px;
            background: rgba(0,255,136,0.1);
            border: 1px solid {grade_color}44;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            color: {grade_color};
        }}

        /* STAT CARDS */
        .stat-cards {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}
        .stat-card {{
            background: rgba(15,23,42,0.8);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 20px;
            transition: border-color 0.2s;
        }}
        .stat-card:hover {{ border-color: rgba(0,255,136,0.2); }}
        .stat-card .icon {{
            font-size: 22px;
            margin-bottom: 12px;
        }}
        .stat-card .val {{
            font-size: 32px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1;
        }}
        .stat-card .lbl {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 6px;
        }}

        /* SECTIONS */
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}
        .section {{
            background: rgba(15,23,42,0.8);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 24px;
        }}
        .section-title {{
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .section-title::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(255,255,255,0.06);
        }}

        /* TACTIC BARS */
        .tactic-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
        }}
        .tactic-name {{
            font-size: 12px;
            color: #94a3b8;
            width: 160px;
            flex-shrink: 0;
        }}
        .bar-track {{
            flex: 1;
            height: 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.8s ease;
            box-shadow: 0 0 8px currentColor;
        }}
        .tactic-pct {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 600;
            width: 40px;
            text-align: right;
        }}

        /* TABLE */
        .table-section {{
            margin-bottom: 24px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            font-size: 10px;
            font-weight: 600;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        td {{
            padding: 14px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            font-size: 13px;
        }}
        tr:hover td {{ background: rgba(255,255,255,0.02); }}
        .technique-id {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #00b4d8;
            background: rgba(0,180,216,0.1);
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .technique-name {{ font-weight: 500; }}
        .tactic-tag {{
            font-size: 11px;
            color: #94a3b8;
            background: rgba(255,255,255,0.05);
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 20px;
            letter-spacing: 1px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .badge-detected {{
            background: rgba(0,255,136,0.1);
            color: #00ff88;
            border: 1px solid rgba(0,255,136,0.2);
        }}
        .badge-missed {{
            background: rgba(255,77,77,0.1);
            color: #ff4d4d;
            border: 1px solid rgba(255,77,77,0.2);
        }}
        .score-max {{ color: #475569; font-size: 11px; }}
        .timestamp {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #475569;
        }}

        /* GAPS */
        .gap-item {{
            padding: 10px 14px;
            background: rgba(255,77,77,0.06);
            border: 1px solid rgba(255,77,77,0.15);
            border-radius: 8px;
            color: #ff4d4d;
            font-size: 13px;
            margin-bottom: 8px;
        }}
        .no-gap {{
            padding: 14px;
            background: rgba(0,255,136,0.05);
            border: 1px solid rgba(0,255,136,0.15);
            border-radius: 8px;
            color: #00ff88;
            font-size: 13px;
        }}

        /* CHART */
        .chart-container {{
            position: relative;
            height: 220px;
        }}

        /* FOOTER */
        .footer {{
            text-align: center;
            padding-top: 24px;
            border-top: 1px solid rgba(255,255,255,0.05);
            font-size: 11px;
            color: #334155;
            font-family: 'JetBrains Mono', monospace;
        }}
    </style>
</head>
<body>
<div class="bg-grid"></div>
<div class="container">

    <!-- HEADER -->
    <div class="header">
        <div class="logo">
            <div class="logo-icon">⚡</div>
            <div class="logo-text">
                <h1>ControlProbe</h1>
                <span>Adaptive Security Control Validator</span>
            </div>
        </div>
        <div class="header-meta">
            <div class="report-id">RPT-{report['report_id']}</div>
            <div class="report-time">{report['generated_at'][:19].replace('T', ' ')} UTC</div>
        </div>
    </div>

    <!-- SCORE HERO -->
    <div class="score-hero">
        <div class="score-card">
            <div class="score-number">{pct}<span style="font-size:32px">%</span></div>
            <div class="score-label">ATT&CK Coverage</div>
            <div class="grade-badge">{summary['grade']}</div>
        </div>
        <div class="stat-cards">
            <div class="stat-card">
                <div class="icon">🎯</div>
                <div class="val">{summary['total_techniques_tested']}</div>
                <div class="lbl">Techniques Tested</div>
            </div>
            <div class="stat-card">
                <div class="icon">✅</div>
                <div class="val" style="color:#00ff88">{summary['detected']}</div>
                <div class="lbl">Controls Detected</div>
            </div>
            <div class="stat-card">
                <div class="icon">⚠️</div>
                <div class="val" style="color:#ff4d4d">{summary['missed']}</div>
                <div class="lbl">Coverage Gaps</div>
            </div>
        </div>
    </div>

    <!-- TACTIC + RADAR -->
    <div class="grid-2">
        <div class="section">
            <div class="section-title">📊 Tactic Coverage Breakdown</div>
            {tactic_rows}
        </div>
        <div class="section">
            <div class="section-title">📡 Coverage Radar</div>
            <div class="chart-container">
                <canvas id="radarChart"></canvas>
            </div>
        </div>
    </div>

    <!-- RESULTS TABLE -->
    <div class="section table-section">
        <div class="section-title">🔍 Technique Simulation Results</div>
        <table>
            <thead>
                <tr>
                    <th>ATT&CK ID</th>
                    <th>Technique</th>
                    <th>Tactic</th>
                    <th>Control Status</th>
                    <th>Score</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>{result_rows}</tbody>
        </table>
    </div>

    <!-- GAPS -->
    <div class="section" style="margin-bottom:24px">
        <div class="section-title">⛔ Coverage Gaps</div>
        {gap_items}
    </div>

    <div class="footer">
        ControlProbe v1.0 — Built on Debian ARM64 — MITRE ATT&amp;CK Framework
    </div>
</div>

<script>
const ctx = document.getElementById('radarChart').getContext('2d');
new Chart(ctx, {{
    type: 'radar',
    data: {{
        labels: {json.dumps(tactic_labels)},
        datasets: [{{
            label: 'Coverage %',
            data: {json.dumps(tactic_values)},
            backgroundColor: 'rgba(0,255,136,0.1)',
            borderColor: '#00ff88',
            borderWidth: 2,
            pointBackgroundColor: '#00ff88',
            pointRadius: 4,
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
            r: {{
                min: 0, max: 100,
                ticks: {{ display: false }},
                grid: {{ color: 'rgba(255,255,255,0.05)' }},
                angleLines: {{ color: 'rgba(255,255,255,0.05)' }},
                pointLabels: {{ color: '#64748b', font: {{ size: 10 }} }}
            }}
        }},
        plugins: {{ legend: {{ display: false }} }}
    }}
}});
</script>
</body>
</html>"""

@app.get("/api/report")
def api_report():
    return get_latest_report()
