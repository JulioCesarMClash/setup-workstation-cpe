$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) {
  & py "$RootDir/scripts/bootstrap.py" @args
  exit $LASTEXITCODE
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
  throw 'Python is required to run bootstrap.py'
}

& python "$RootDir/scripts/bootstrap.py" @args
exit $LASTEXITCODE
