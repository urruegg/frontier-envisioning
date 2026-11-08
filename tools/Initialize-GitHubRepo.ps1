<#
.SYNOPSIS
  Create and configure the frontier-envisioning GitHub repository and seed the intake backlog.
.DESCRIPTION
  Thin wrapper around tools/bootstrap_github.py (the logic is in Python so it runs and is tested on every platform).
  Runs a dry run first, shows the plan, and applies it only after you confirm.
  Needs Python 3.11+, Git and the GitHub CLI (gh auth login).
.EXAMPLE
  ./tools/Initialize-GitHubRepo.ps1 -Owner urruegg
.EXAMPLE
  ./tools/Initialize-GitHubRepo.ps1 -Owner my-org -Visibility internal -Approvals 1
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$Owner,
  [string]$Repo = "frontier-envisioning",
  [ValidateSet("private", "internal", "public")][string]$Visibility = "private",
  [int]$Approvals = 1,
  [switch]$SkipIssues
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
  $python = (Get-Command python -ErrorAction SilentlyContinue) ?? (Get-Command python3 -ErrorAction SilentlyContinue)
  if (-not $python) { throw "Python 3.11 or later is required." }
  $common = @("tools/bootstrap_github.py", "--owner", $Owner, "--repo", $Repo, "--visibility", $Visibility, "--approvals", "$Approvals")
  if ($SkipIssues) { $common += "--skip-issues" }
  & $python.Source @common
  if ($LASTEXITCODE -ne 0) { throw "Dry run failed." }
  $answer = Read-Host "Apply these changes to $Owner/$Repo? (yes/no)"
  if ($answer -ne "yes") { Write-Host "Nothing changed."; return }
  & $python.Source @common "--apply"
  if ($LASTEXITCODE -ne 0) { throw "Bootstrap failed." }
}
finally { Pop-Location }
