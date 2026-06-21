import json
import os
from datetime import datetime

class Reporter:
    def generate(self, results, coverage):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/report_{timestamp}.json"

        report = {
            "report_id": timestamp,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "coverage_percentage": coverage["coverage_percentage"],
                "grade": coverage["grade"],
                "total_techniques_tested": coverage["total_techniques"],
                "detected": coverage["detected"],
                "missed": coverage["missed"]
            },
            "tactic_coverage": coverage["tactic_coverage"],
            "gaps": coverage["gaps"],
            "results": results
        }

        os.makedirs("reports", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        self.print_summary(coverage, filename)

    def print_summary(self, coverage, filename):
        print("=" * 50)
        print("        CONTROLPROBE COVERAGE REPORT")
        print("=" * 50)
        print(f"  Coverage Score : {coverage['coverage_percentage']}%")
        print(f"  Grade          : {coverage['grade']}")
        print(f"  Detected       : {coverage['detected']}/{coverage['total_techniques']}")
        print(f"  Missed         : {coverage['missed']}")
        print()
        print("  Tactic Coverage:")
        for tactic, pct in coverage["tactic_coverage"].items():
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            print(f"  {tactic:<25} {bar} {pct}%")
        print()
        if coverage["gaps"]:
            print("  Gaps Detected:")
            for gap in coverage["gaps"]:
                print(f"  ✗ {gap}")
        else:
            print("  ✓ No gaps detected")
        print()
        print(f"  Report saved: {filename}")
        print("=" * 50)
