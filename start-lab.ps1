Set-Location -LiteralPath $PSScriptRoot
$labPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (Test-Path -LiteralPath $labPython) {
    & $labPython run.py --open @args
} else {
    python run.py --open @args
}
