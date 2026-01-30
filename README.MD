# Cloud Advisory Copilot (Cloud-Agnostic)

A FastAPI-based advisory service that takes a workload intake form and returns a scorecard + prioritized recommendations.

 - Day 1 includes API scaffolding and a stub engine.  (comp 01/27)

 - Day 2 adds YAML rule loading and matching. (comp 01/28)

 - Day 3 adds weighted scoring to the different scored components, produces a recommendation

## Run locally
```bash
python -m venv .venv
# Windows PowerShell:
. .venv\Scripts\Activate.ps1
pip install - requirements.txt
uvicorn app.main:app --reload#   c l o u d - a d v i s o r y - c o p i l o t  
 