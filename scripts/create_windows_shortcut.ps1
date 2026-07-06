param(
    [string]$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [int]$Port = 8501,
    [switch]$Remove
)

$ErrorActionPreference = "Stop"
$ShortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "AI Workflow Risk Auditor Pro.lnk"

if ($Port -lt 1 -or $Port -gt 65535) {
    throw "Port must be between 1 and 65535."
}

if ($Remove) {
    if (Test-Path $ShortcutPath) {
        Remove-Item -LiteralPath $ShortcutPath
        Write-Host "Removed $ShortcutPath"
    } else {
        Write-Host "No AIWRA desktop shortcut was found."
    }
    exit 0
}

$Python = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$App = Join-Path $ProjectDir "app.py"
$Icon = Join-Path $ProjectDir "assets\aiwra_icon.svg"

if (-not (Test-Path $App)) { throw "app.py was not found in $ProjectDir" }
if (-not (Test-Path $Python)) { throw "The virtual environment is missing. Create .venv and install requirements first." }
& $Python -c "import streamlit"
if ($LASTEXITCODE -ne 0) { throw "Streamlit is unavailable in .venv. Install requirements first." }

$EscapedProject = $ProjectDir.Replace("'", "''")
$EscapedPython = $Python.Replace("'", "''")
$EscapedApp = $App.Replace("'", "''")
$Command = "Set-Location -LiteralPath '$EscapedProject'; Start-Process 'http://127.0.0.1:$Port'; & '$EscapedPython' -m streamlit run '$EscapedApp' --server.address 127.0.0.1 --server.port $Port --server.headless true --browser.gatherUsageStats false"

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -NoExit -Command `"$Command`""
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = "AI Workflow Risk Auditor Pro - local-only Streamlit launcher"
$Shortcut.Save()

Write-Host "Created $ShortcutPath"
Write-Host "The app binds only to http://127.0.0.1:$Port. No administrator rights are required."
Write-Host "Note: Windows shortcut icons generally require .ico; the local SVG remains the canonical app asset."
