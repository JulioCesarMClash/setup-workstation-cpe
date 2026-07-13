$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$EnvFile = Join-Path $RootDir ".env"
$EnvExample = Join-Path $RootDir ".env.example"

if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
  Copy-Item $EnvExample $EnvFile
  Write-Host 'Created .env from .env.example'
}

function Resolve-Python {
  $Py = Get-Command py -ErrorAction SilentlyContinue
  if ($Py) { return @('py') }

  $Python = Get-Command python -ErrorAction SilentlyContinue
  if ($Python) { return @('python') }

  Write-Host 'Python not found. Attempting installation...'

  $Winget = Get-Command winget -ErrorAction SilentlyContinue
  if ($Winget) {
    & winget install -e --id Python.Python.3.12
  }
  else {
    $Choco = Get-Command choco -ErrorAction SilentlyContinue
    if ($Choco) {
      & choco install python -y
    }
    else {
      $Scoop = Get-Command scoop -ErrorAction SilentlyContinue
      if ($Scoop) {
        & scoop install python
      }
      else {
        throw 'Python is required and no supported Windows package manager was found to install it automatically.'
      }
    }
  }

  $Py = Get-Command py -ErrorAction SilentlyContinue
  if ($Py) { return @('py') }

  $Python = Get-Command python -ErrorAction SilentlyContinue
  if ($Python) { return @('python') }

  throw 'Python installation did not produce a runnable executable on PATH.'
}

$PythonCmd = Resolve-Python
& $PythonCmd[0] "$RootDir/scripts/bootstrap.py" @args
exit $LASTEXITCODE
