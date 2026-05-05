import json
from pathlib import Path


def evaluate_slos(metrics_payload: dict) -> dict:
    service = metrics_payload["service"]
    metrics = metrics_payload["metrics"]
    slos = metrics_payload["slos"]

    findings = []
    recommendations = []

    score = 100

    availability = metrics["availability_percent"]
    latency = metrics["p95_latency_ms"]
    error_rate = metrics["error_rate_percent"]

    if availability < slos["availability_percent"]:
        score -= 20
        findings.append(
            f"Availability is below SLO: {availability}% < {slos['availability_percent']}%"
        )
        recommendations.append(
            "Investigate recent deploys, failing health checks, dependency outages, and load balancer target health."
        )

    if latency > slos["p95_latency_ms"]:
        score -= 20
        findings.append(
            f"P95 latency is above SLO: {latency}ms > {slos['p95_latency_ms']}ms"
        )
        recommendations.append(
            "Review slow endpoints, database queries, autoscaling settings, and upstream service latency."
        )

    if error_rate > slos["error_rate_percent"]:
        score -= 20
        findings.append(
            f"Error rate is above SLO: {error_rate}% > {slos['error_rate_percent']}%"
        )
        recommendations.append(
            "Check application logs, recent releases, exception patterns, and dependency failures."
        )

    if metrics.get("cpu_utilization_percent", 0) > 75:
        score -= 10
        recommendations.append(
            "CPU utilization is high. Consider horizontal scaling or reviewing CPU-heavy code paths."
        )

    if metrics.get("memory_utilization_percent", 0) > 75:
        score -= 10
        recommendations.append(
            "Memory utilization is high. Check for memory leaks, oversized workloads, or insufficient limits."
        )

    status = "healthy" if not findings else "at_risk"

    if score >= 80:
        severity = "low"
    elif score >= 50:
        severity = "medium"
    else:
        severity = "high"

    return {
        "service": service,
        "status": status,
        "reliability_score": max(score, 0),
        "severity": severity,
        "findings": findings,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    metrics_file = Path("examples/metrics_sample.json")

    with metrics_file.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    result = evaluate_slos(payload)

    print(json.dumps(result, indent=2))