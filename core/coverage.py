class CoverageCalculator:
    def calculate(self, results):
        total = len(results)
        detected = sum(1 for r in results if r["detected"])
        missed = total - detected
        percentage = round((detected / total) * 100, 1) if total > 0 else 0

        tactics = {}
        for r in results:
            tactic = r["tactic"]
            if tactic not in tactics:
                tactics[tactic] = {"total": 0, "detected": 0}
            tactics[tactic]["total"] += 1
            if r["detected"]:
                tactics[tactic]["detected"] += 1

        tactic_coverage = {}
        for tactic, data in tactics.items():
            tactic_coverage[tactic] = round(
                (data["detected"] / data["total"]) * 100, 1
            )

        gaps = [
            r["technique_id"] + " — " + r["technique_name"]
            for r in results if not r["detected"]
        ]

        return {
            "total_techniques": total,
            "detected": detected,
            "missed": missed,
            "coverage_percentage": percentage,
            "tactic_coverage": tactic_coverage,
            "gaps": gaps,
            "grade": self.grade(percentage)
        }

    def grade(self, percentage):
        if percentage >= 90:
            return "A — Excellent"
        elif percentage >= 70:
            return "B — Good"
        elif percentage >= 50:
            return "C — Needs Improvement"
        else:
            return "D — Critical Gaps"
