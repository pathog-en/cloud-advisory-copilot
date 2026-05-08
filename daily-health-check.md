# Daily SRE Health Check - Cloud Advisory Copilot

## Goal
Confirm that the Cloud Advisory Copilot API is available, healthy, and producing valid advisory recommendations.

## Checks

### 1. Start or confirm the service is running

```powershell
uvicorn app.main:app --reload