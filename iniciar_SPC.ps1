param(
    [switch]$SemNavegador
)

$Host.UI.RawUI.BackgroundColor = "DarkCyan"
try { $Host.UI.RawUI.WindowTitle = "SPC - Sistema de Prestacao de Contas" } catch { }
Clear-Host

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = $PSScriptRoot
if (-not $Root) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path }
$Root = (Resolve-Path -LiteralPath $Root).Path
Set-Location -LiteralPath $Root

$EntryFile = Join-Path $Root "SPC.py"
$Porta = 5735
$UrlAcesso = "http://127.0.0.1:$Porta"
$VenvPython = Join-Path $Root "SPC_venv\Scripts\python.exe"

function Wait-IfInteractive {
    if ($SemNavegador) { return }
    if ($Host.Name -eq "ConsoleHost") {
        Write-Host ""
        Write-Host "Pressione Enter para fechar..." -ForegroundColor Yellow
        try { [void](Read-Host) } catch { }
    }
}

function Test-PortaEmUso {
    param([int]$Numero)
    try {
        $listeners = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
        return [bool]($listeners | Where-Object { $_.Port -eq $Numero })
    } catch {
        return $false
    }
}

if (-not (Test-Path -LiteralPath $EntryFile)) {
    Write-Host "ERRO: SPC.py nao encontrado em $Root" -ForegroundColor Red
    Wait-IfInteractive
    exit 1
}
if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "ERRO: ambiente SPC_venv nao encontrado." -ForegroundColor Red
    Write-Host "Execute instalar_servico.ps1 primeiro." -ForegroundColor Yellow
    Wait-IfInteractive
    exit 1
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SPC - Sistema de Prestacao de Contas" -ForegroundColor Green
Write-Host "Prefeitura Municipal de Cosmopolis - SP" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Acesso : $UrlAcesso" -ForegroundColor Gray
Write-Host ""

if (Test-PortaEmUso -Numero $Porta) {
    Write-Host "O SPC ja esta em execucao na porta $Porta." -ForegroundColor Yellow
    if (-not $SemNavegador) { Start-Process $UrlAcesso }
    Wait-IfInteractive
    exit 0
}

if (-not $SemNavegador) {
    Start-Job { Start-Sleep -Seconds 3; Start-Process "http://127.0.0.1:5735" } | Out-Null
}

& $VenvPython $EntryFile
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Host "O SPC encerrou com codigo $exitCode." -ForegroundColor Red
    Wait-IfInteractive
}
exit $exitCode
