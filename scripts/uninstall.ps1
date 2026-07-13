$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) {
  & py "$RootDir/scripts/uninstall.py" @args
  exit $LASTEXITCODE
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
  throw 'Python is required to run uninstall.py'
}

& python "$RootDir/scripts/uninstall.py" @args
exit $LASTEXITCODE
