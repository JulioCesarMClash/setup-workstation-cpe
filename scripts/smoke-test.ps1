$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) {
  & py "$RootDir/scripts/smoke_test.py" @args
  exit $LASTEXITCODE
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
  throw 'Python is required to run smoke_test.py'
}

& python "$RootDir/scripts/smoke_test.py" @args
exit $LASTEXITCODE
