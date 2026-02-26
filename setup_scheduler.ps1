# AI News Aggregator - Windows Task Scheduler Setup Script
# Run this script as Administrator.

Write-Host "AI News Aggregator - Task Scheduler Setup"
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "This script must be run as Administrator."
    Write-Host "Right-click PowerShell and select 'Run as administrator'."
    exit 1
}

# Get user input
$taskName = Read-Host "Task name (default: 'AI News Digest Daily')"
if (-not $taskName) { $taskName = "AI News Digest Daily" }

$hour = Read-Host "What hour to run? (0-23, default: 9)"
if (-not $hour) { $hour = 9 }
if ($hour -lt 0 -or $hour -gt 23) { $hour = 9 }

$minute = Read-Host "What minute? (0-59, default: 0)"
if (-not $minute) { $minute = 0 }
if ($minute -lt 0 -or $minute -gt 59) { $minute = 0 }

$time = "{0:D2}:{1:D2}:00" -f $hour, $minute

# Get current script directory (workshop folder)
$workDir = $PSScriptRoot
if (-not (Test-Path "$workDir\ai_news_agent.py")) {
    $workDir = Read-Host "Path to workshop folder (containing ai_news_agent.py)"
}

if (-not (Test-Path "$workDir\ai_news_agent.py")) {
    Write-Host "ai_news_agent.py not found in: $workDir"
    exit 1
}

Write-Host "Creating scheduled task..."

try {
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    $action = New-ScheduledTaskAction -Execute "python" -Argument "ai_news_agent.py" -WorkingDirectory $workDir
    $trigger = New-ScheduledTaskTrigger -Daily -At $time
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null

    Write-Host "Task created successfully."
    Write-Host "Name: $taskName"
    Write-Host "Schedule: Daily at $time"
    Write-Host "Working directory: $workDir"
} catch {
    Write-Host "Error creating task: $_"
    exit 1
}

Write-Host ""
Write-Host "You can run it now with:"
Write-Host "  Start-ScheduledTask -TaskName '$taskName'"
