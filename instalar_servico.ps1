# Instala o ambiente SPC_venv, o icone, o atalho SPC e o servico Windows.
# A criacao do servico exige PowerShell elevado.

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
if (-not $Root) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path }
$Root = (Resolve-Path -LiteralPath $Root).Path
Set-Location -LiteralPath $Root

$Venv = Join-Path $Root "SPC_venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$Servico = "SPC-SistemaPrestacaoContas"

Write-Host "Preparando o ambiente SPC_venv..." -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath $Python)) {
    py -3 -m venv $Venv
}
& $Python -m pip install --upgrade pip
& $Python -m pip install -r (Join-Path $Root "requirements.txt")

$Icone = Join-Path $Root "static\img\Favicon.ico"
& $Python -c @"
from PIL import Image
from pathlib import Path
origem = Path(r'$Root') / 'Favicon.png'
destino = Path(r'$Icone')
imagem = Image.open(origem).convert('RGBA')
destino.parent.mkdir(parents=True, exist_ok=True)
imagem.save(destino, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)])
print(destino)
"@

$Desktop = [Environment]::GetFolderPath("Desktop")
$Atalho = Join-Path $Desktop "SPC.lnk"
$Shell = New-Object -ComObject WScript.Shell
$Lnk = $Shell.CreateShortcut($Atalho)
$Lnk.TargetPath = "powershell.exe"
$Lnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$Root\iniciar_SPC.ps1`""
$Lnk.WorkingDirectory = $Root
$Lnk.IconLocation = "$Icone,0"
$Lnk.Description = "SPC - Sistema de Prestacao de Contas"
$Lnk.WindowStyle = 1
$Lnk.Save()
Write-Host "Atalho criado em $Atalho" -ForegroundColor Green

$Servicos = Join-Path $Desktop "SERVIÇOS"
if (Test-Path -LiteralPath $Servicos) {
    Copy-Item -LiteralPath $Atalho -Destination (Join-Path $Servicos "SPC.lnk") -Force
    Write-Host "Atalho tambem copiado para a pasta SERVIÇOS." -ForegroundColor Green
}

$ehAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)
if (-not $ehAdmin) {
    Write-Host "O atalho foi criado. Para registrar o servico $Servico, execute este script como administrador." -ForegroundColor Yellow
    exit 0
}

& $Python (Join-Path $Root "servico_windows.py") --startup auto install
& $Python (Join-Path $Root "servico_windows.py") start
Write-Host "Servico $Servico instalado e iniciado." -ForegroundColor Green
