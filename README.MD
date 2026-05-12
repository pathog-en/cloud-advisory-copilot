# Cloud Advisory Copilot

## Overview

Cloud Advisory Copilot is a FastAPI-based service that evaluates cloud workloads and provides structured recommendations across key domains:

- Cost
- Security
- Reliability
- Performance
- Operations

The system transforms cloud best practices into a **repeatable, rules-based advisory engine**.

---

## Problem

Cloud teams often understand best practices, but struggle to consistently apply them across workloads.

This leads to:

- inconsistent architecture decisions
- missed security controls
- inefficient cost management
- lack of standardized evaluation

---

## Solution

This project provides:

- a standardized workload input schema
- a rules-based evaluation engine (YAML-driven)
- a scoring system across cloud domains
- prioritized recommendations

---

## Architecture


Client → FastAPI (/assess)
→ Input normalization
→ Rules engine (YAML)
→ Scoring + recommendations
→ JSON response


---

## Example Response

```json
{
  "scores": {
    "cost": 70,
    "security": 84,
    "reliability": 70,
    "performance": 70,
    "operations": 70
  },
  "recommendations": [
    {
      "id": "SEC-002",
      "priority": "P0",
      "title": "Encrypt data in transit and at rest"
    }
  ]
}


```
---

## SRE Validation

This project includes a daily SRE validation script:

scripts/daily-sre-check.ps1
What it checks
API availability (/health)
Functional correctness (/assess)
Output completeness (scores + recommendations)
Rules engine integrity (rules loaded)
Performance (latency thresholds)
Example
.\scripts\daily-sre-check.ps1
CI/CD Integration

---

## The SRE validation is integrated into GitHub Actions:

Runs on every push
Fails if:
API is unreachable
payload is invalid
rules are missing
latency exceeds thresholds
Failure Testing

---

## The system has been validated against multiple failure scenarios:

service outage
missing input file
invalid API payload
latency degradation
missing rules engine
Cloud Engineering Principles
Standardized workload modeling
Separation of concerns (API, rules engine, config)
Configuration-driven logic (YAML rules)
Cloud-agnostic evaluation model
SRE / Platform Engineering Concepts
synthetic validation (not just health checks)
service-level expectations (latency thresholds)
failure-mode testing
CI-based operational validation

---

## Future Enhancements:

expanded rule library
multi-workload test scenarios
historical scoring + trend analysis
integration with real cloud environments
UI dashboard for advisory output

## Getting Started ##

## Install dependencies
pip install -r requirements.txt

## Run the API
python -m uvicorn app.main:app

## Run SRE validation
.\scripts\daily-sre-check.ps1

## Architecture Overview
 ![Architecture Diagram](docs/architecture.png)
