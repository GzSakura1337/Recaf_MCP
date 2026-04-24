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
$pluginUrl = "http://$RecafHost`:$RecafPort/health"
$mcpUrl = "http://$ListenHost`:$Port/mcp"

function Test-HttpUrl {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    } catch {
        return $false
    }
}

if ($Foreground) {
    & $python @args
    exit $LASTEXITCODE
}

if (-not (Test-HttpUrl $pluginUrl)) {
    Write-Error "Recaf plugin is not reachable at $pluginUrl. Start Recaf first and confirm the plugin loaded."
    exit 1
}

$existing = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match "^python" -and $_.CommandLine -match "recaf_mcp_server.py" -and $_.CommandLine -match "--http" }

if ($existing) {
    [pscustomobject]@{
        ProcessId = $existing[0].ProcessId
        Url = $mcpUrl
        PluginHealth = $pluginUrl
        Note = "Server already running. Open a new Codex chat in this folder to load recaf-mcp tools."
    }
    exit 0
}

$stdout = Join-Path $root "recaf_mcp_http.out.log"
$stderr = Join-Path $root "recaf_mcp_http.err.log"

$process = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $root `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 2
[pscustomobject]@{
    ProcessId = $process.Id
    Url = $mcpUrl
    PluginHealth = $pluginUrl
    Stdout = $stdout
    Stderr = $stderr
    Note = "If Codex does not show 'Used recaf-mcp', open a new chat after this server is up."
}
