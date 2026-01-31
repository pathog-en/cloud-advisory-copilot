# Cloud Advisory Copilot (Cloud-Agnostic)

A FastAPI-based advisory service that takes a workload intake form and returns a scorecard + prioritized recommendations.

 - Day 1 includes API scaffolding and a stub engine.  (comp 01/27)

 - Day 2 adds YAML rule loading and matching. (comp 01/28)

 - Day 3 adds weighted scoring to the different scored components, produces a recommendation (comp 01/29)
 
 - Day 4 adds in rule matching, what should be done/actions taken when scores are produced, how the scores change.  Assessments get rendered as a markdown file.

## Run locally (Windows PowerShell)

python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app

 
 