$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$RootDir/scripts/bootstrap.ps1" @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& "$RootDir/scripts/smoke-test.ps1"
exit $LASTEXITCODE
