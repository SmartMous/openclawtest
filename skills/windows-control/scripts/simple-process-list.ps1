#!/usr/bin/env pwsh
# 简单的进程列表脚本

Write-Host "=== Windows 进程列表 ===" -ForegroundColor Green

# 获取前10个CPU使用率最高的进程
$processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10

foreach ($process in $processes) {
    $cpu = [math]::Round($process.CPU, 2)
    $memory = [math]::Round($process.WorkingSet / 1MB, 2)
    
    Write-Host "ID: $($process.Id)" -ForegroundColor Cyan -NoNewline
    Write-Host " | 名称: $($process.ProcessName)" -ForegroundColor White -NoNewline
    Write-Host " | CPU: ${cpu}%" -ForegroundColor Yellow -NoNewline
    Write-Host " | 内存: ${memory} MB" -ForegroundColor Magenta
}

# 统计信息
$total = (Get-Process).Count
$totalMemory = [math]::Round((Get-Process | Measure-Object WorkingSet -Sum).Sum / 1MB, 2)

Write-Host "`n=== 统计 ===" -ForegroundColor Green
Write-Host "总进程数: $total" -ForegroundColor White
Write-Host "总内存使用: ${totalMemory} MB" -ForegroundColor White