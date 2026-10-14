# Cria a tarefa que liga o bot sozinho quando voce entra no Windows.
# Uso (na raiz do projeto):  powershell -ExecutionPolicy Bypass -File scripts\instalar_inicio_windows.ps1
# Para remover:              Unregister-ScheduledTask -TaskName InstagramUtilBot -Confirm:$false

$ErrorActionPreference = "Stop"
$nome = "InstagramUtilBot"
$pasta = Split-Path -Parent $PSScriptRoot
# pythonw roda sem janela de terminal.
$pythonw = Join-Path $pasta ".venv\Scripts\pythonw.exe"

if (-not (Test-Path $pythonw)) {
    throw "Nao achei $pythonw. Rode 'uv sync' na pasta do projeto primeiro."
}
if (-not (Test-Path (Join-Path $pasta ".env"))) {
    throw "Nao achei o arquivo .env. Copie .env.example para .env e preencha."
}

$acao = New-ScheduledTaskAction -Execute $pythonw -Argument "main.py" -WorkingDirectory $pasta
$gatilho = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
# Sem limite de tempo; se o bot cair, o Windows religa ate 3 vezes, 1 minuto entre elas.
$configuracao = New-ScheduledTaskSettingsSet `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $nome -Action $acao -Trigger $gatilho `
    -Settings $configuracao -Force | Out-Null

Write-Host "Tarefa '$nome' criada. O bot liga na proxima vez que voce entrar no Windows."
Write-Host "Para ligar agora:   Start-ScheduledTask -TaskName $nome"
Write-Host "Para parar:         Stop-ScheduledTask -TaskName $nome"
