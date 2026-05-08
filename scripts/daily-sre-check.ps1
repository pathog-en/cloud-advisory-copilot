# daily-sre-check.ps1
#
# Purpose:
# Runs a daily SRE validation check against the Cloud Advisory Copilot API.
#
# This script validates more than basic availability. It checks:
# 1. Required test payload exists
# 2. /health endpoint is reachable
# 3. /assess endpoint accepts a known-good workload
# 4. Response includes all expected score fields
# 5. Response includes recommendations
# 6. Rules engine reports loaded rules
# 7. Health and assess response times are captured
#
# Exit codes:
# 0 = PASS
# 1 = FAIL
#
# This makes the script usable locally and in CI/CD systems such as GitHub Actions.

$ErrorActionPreference = "Stop"

$BaseUrl = "http://127.0.0.1:8000"
$HealthUrl = "$BaseUrl/health"
$AssessUrl = "$BaseUrl/assess"
$PayloadPath = "examples/sample-workload.json"

$OverallStart = Get-Date

Write-Host ""
Write-Host "========================================"
Write-Host " Cloud Advisory Copilot - Daily SRE Check"
Write-Host "========================================"
Write-Host ""

# -------------------------------
# Helper: fail fast with exit code
# -------------------------------

function Fail-Check {
    param (
        [string]$Message
    )

    Write-Host "FAIL: $Message" -ForegroundColor Red
    Write-Host ""
    Write-Host "Daily SRE Check Result: FAIL" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# -------------------------------
# Check 1: Confirm sample payload exists
# -------------------------------

Write-Host "[1/5] Checking for sample workload file..."

if (-Not (Test-Path $PayloadPath)) {
    Fail-Check "Sample workload file not found at $PayloadPath"
}

Write-Host "PASS: Sample workload file found." -ForegroundColor Green

# -------------------------------
# Check 2: Health endpoint
# -------------------------------

Write-Host ""
Write-Host "[2/5] Checking /health endpoint..."

try {
    $HealthStart = Get-Date

    $HealthResponse = Invoke-RestMethod `
        -Uri $HealthUrl `
        -Method GET

    $HealthEnd = Get-Date
    $HealthDurationMs = [math]::Round(($HealthEnd - $HealthStart).TotalMilliseconds, 2)

    if ($HealthResponse.status -eq "ok") {
        Write-Host "PASS: /health returned status=ok." -ForegroundColor Green
        Write-Host "INFO: /health response time: $HealthDurationMs ms"
    }
    else {
        Write-Host "Response:"
        $HealthResponse | ConvertTo-Json -Depth 10
        Fail-Check "/health responded, but status was not ok."
    }
}
catch {
    Write-Host "Could not reach /health endpoint."
    Write-Host "Is the API running with the command below?"
    Write-Host ""
    Write-Host "python -m uvicorn app.main:app --reload"
    Write-Host ""
    Write-Host "Error:"
    Write-Host $_.Exception.Message
    Fail-Check "/health endpoint check failed."
}

# -------------------------------
# Check 3: Assess endpoint
# -------------------------------

Write-Host ""
Write-Host "[3/5] Checking /assess endpoint with sample workload..."

try {
    $AssessStart = Get-Date

    $AssessResponse = Invoke-RestMethod `
        -Uri $AssessUrl `
        -Method POST `
        -Headers @{ "Content-Type" = "application/json" } `
        -InFile $PayloadPath

    $AssessEnd = Get-Date
    $AssessDurationMs = [math]::Round(($AssessEnd - $AssessStart).TotalMilliseconds, 2)
}
catch {
    Write-Host "Error:"
    Write-Host $_.Exception.Message
    Fail-Check "/assess request failed."
}

Write-Host "PASS: /assess returned a response." -ForegroundColor Green
Write-Host "INFO: /assess response time: $AssessDurationMs ms"

# -------------------------------
# Check 4: Validate scores
# -------------------------------

Write-Host ""
Write-Host "[4/5] Validating score output..."

if ($null -eq $AssessResponse.scores) {
    Fail-Check "Response did not include scores."
}

$ScoreFields = @("cost", "security", "reliability", "performance", "operations")

foreach ($Field in $ScoreFields) {
    if ($null -eq $AssessResponse.scores.$Field) {
        Fail-Check "Missing score field: $Field"
    }
}

Write-Host "PASS: All expected score fields were returned." -ForegroundColor Green

# -------------------------------
# Check 5: Validate recommendations and rules
# -------------------------------

Write-Host ""
Write-Host "[5/5] Validating recommendations and rules engine..."

if ($null -eq $AssessResponse.recommendations -or $AssessResponse.recommendations.Count -eq 0) {
    Fail-Check "No recommendations were returned."
}

if ($null -eq $AssessResponse.meta.rules_loaded -or $AssessResponse.meta.rules_loaded -lt 1) {
    Fail-Check "Rules engine did not report loaded rules."
}

Write-Host "PASS: Recommendations returned." -ForegroundColor Green
Write-Host "PASS: Rules loaded: $($AssessResponse.meta.rules_loaded)" -ForegroundColor Green

# -------------------------------
# Summary
# -------------------------------

$OverallEnd = Get-Date
$OverallDurationMs = [math]::Round(($OverallEnd - $OverallStart).TotalMilliseconds, 2)

Write-Host ""
Write-Host "========================================"
Write-Host " Daily SRE Check Result: PASS"
Write-Host "========================================"
Write-Host ""

Write-Host "Scores:"
Write-Host "  Cost:        $($AssessResponse.scores.cost)"
Write-Host "  Security:    $($AssessResponse.scores.security)"
Write-Host "  Reliability: $($AssessResponse.scores.reliability)"
Write-Host "  Performance: $($AssessResponse.scores.performance)"
Write-Host "  Operations:  $($AssessResponse.scores.operations)"

Write-Host ""
Write-Host "Recommendations returned: $($AssessResponse.recommendations.Count)"

foreach ($Rec in $AssessResponse.recommendations) {
    Write-Host "  - [$($Rec.priority)] $($Rec.id): $($Rec.title)"
}

Write-Host ""
Write-Host "Engine version: $($AssessResponse.meta.engine_version)"
Write-Host "Rules loaded:   $($AssessResponse.meta.rules_loaded)"
Write-Host ""
Write-Host "Timing:"
Write-Host "  /health:      $HealthDurationMs ms"
Write-Host "  /assess:      $AssessDurationMs ms"
Write-Host "  Total check:  $OverallDurationMs ms"
Write-Host ""

exit 0