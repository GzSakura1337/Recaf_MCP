param(
    [string]$ListenHost = "127.0.0.1",
    [int]$Port = 8751,
    [string]$RecafHost = "127.0.0.1",
    [int]$RecafPort = 8750,
    [switch]$Foreground
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = (Get-Command python -ErrorAction Stop).Source
$script = Join-Path $root "recaf_mcp_server.py"
$args = @($script, "--http", "--host", $ListenHost, "--port", $Port, "--recaf-host", $RecafHost, "--recaf-port", $RecafPort)

if ($Foreground) {
    & $python @args
    exit $LASTEXITCODE
}

$existing = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match "^python" -and $_.CommandLine -match "recaf_mcp_server.py" -and $_.CommandLine -match "--http" }

if ($existing) {
    $existing | Select-Object ProcessId, CommandLine
    exit 0
}

$stdout = Join-Path $root "recaf_mcp_http.out.log"
$stderr = Join-Path $root "recaf_mcp_http.err.log"

$process = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $root `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 2
[pscustomobject]@{
    ProcessId = $process.Id
    Url = "http://$ListenHost`:$Port/mcp"
    Stdout = $stdout
    Stderr = $stderr
}
