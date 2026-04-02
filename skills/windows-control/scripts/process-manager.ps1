#!/usr/bin/env pwsh
# Windows 进程管理器

param(
    [string]$Action = "list",
    [string]$ProcessName,
    [int]$ProcessId,
    [int]$Top = 10
)

function Show-ProcessList {
    param([int]$TopCount = 10)
    
    Write-Host "=== 进程列表 (前${TopCount}个CPU使用率) ===" -ForegroundColor Green
    
    $processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First $TopCount
    
    $processes | ForEach-Object {
        $cpuPercent = [math]::Round($_.CPU, 2)
        $memoryMB = [math]::Round($_.WorkingSet / 1MB, 2)
        
        Write-Host "进程ID: $($_.Id)" -ForegroundColor Cyan
        Write-Host "  名称: $($_.ProcessName)" -ForegroundColor White
        Write-Host "  CPU: ${cpuPercent}%" -ForegroundColor White
        Write-Host "  内存: ${memoryMB} MB" -ForegroundColor White
        if ($_.StartTime) {
            Write-Host "  启动时间: $($_.StartTime)" -ForegroundColor White
        }
        Write-Host ""
    }
    
    # 统计信息
    $totalProcesses = (Get-Process).Count
    $totalMemory = [math]::Round((Get-Process | Measure-Object WorkingSet -Sum).Sum / 1MB, 2)
    
    Write-Host "=== 统计信息 ===" -ForegroundColor Yellow
    Write-Host "总进程数: ${totalProcesses}" -ForegroundColor White
    Write-Host "总内存使用: ${totalMemory} MB" -ForegroundColor White
}

function Stop-ProcessByName {
    param([string]$Name)
    
    Write-Host "正在停止进程: ${Name}" -ForegroundColor Yellow
    
    $processes = Get-Process -Name $Name -ErrorAction SilentlyContinue
    
    if ($processes) {
        $processes | ForEach-Object {
            Write-Host "  停止进程ID: $($_.Id), 名称: $($_.ProcessName)" -ForegroundColor White
            Stop-Process -Id $_.Id -Force
        }
        Write-Host "进程已停止" -ForegroundColor Green
    } else {
        Write-Host "未找到进程: ${Name}" -ForegroundColor Red
    }
}

function Stop-ProcessById {
    param([int]$Id)
    
    Write-Host "正在停止进程ID: ${Id}" -ForegroundColor Yellow
    
    try {
        $process = Get-Process -Id $Id -ErrorAction Stop
        Write-Host "  进程名称: $($process.ProcessName)" -ForegroundColor White
        Stop-Process -Id $Id -Force
        Write-Host "进程已停止" -ForegroundColor Green
    } catch {
        Write-Host "未找到进程ID: ${Id}" -ForegroundColor Red
    }
}

function Find-Process {
    param([string]$Name)
    
    Write-Host "=== 查找进程: ${Name} ===" -ForegroundColor Green
    
    $processes = Get-Process | Where-Object { $_.ProcessName -like "*${Name}*" }
    
    if ($processes) {
        $processes | ForEach-Object {
            $memoryMB = [math]::Round($_.WorkingSet / 1MB, 2)
            
            Write-Host "进程ID: $($_.Id)" -ForegroundColor Cyan
            Write-Host "  名称: $($_.ProcessName)" -ForegroundColor White
            Write-Host "  CPU: $($_.CPU)%" -ForegroundColor White
            Write-Host "  内存: ${memoryMB} MB" -ForegroundColor White
            if ($_.Path) {
                Write-Host "  路径: $($_.Path)" -ForegroundColor White
            }
            Write-Host ""
        }
    } else {
        Write-Host "未找到包含 '${Name}' 的进程" -ForegroundColor Red
    }
}

# 主逻辑
switch ($Action.ToLower()) {
    "list" {
        Show-ProcessList -TopCount $Top
    }
    "stopbyname" {
        if ($ProcessName) {
            Stop-ProcessByName -Name $ProcessName
        } else {
            Write-Host "请使用 -ProcessName 参数指定进程名称" -ForegroundColor Red
        }
    }
    "stopbyid" {
        if ($ProcessId) {
            Stop-ProcessById -Id $ProcessId
        } else {
            Write-Host "请使用 -ProcessId 参数指定进程ID" -ForegroundColor Red
        }
    }
    "find" {
        if ($ProcessName) {
            Find-Process -Name $ProcessName
        } else {
            Write-Host "请使用 -ProcessName 参数指定查找关键词" -ForegroundColor Red
        }
    }
    default {
        Write-Host "可用操作:" -ForegroundColor Yellow
        Write-Host "  list - 列出进程" -ForegroundColor White
        Write-Host "  stopbyname - 按名称停止进程" -ForegroundColor White
        Write-Host "  stopbyid - 按ID停止进程" -ForegroundColor White
        Write-Host "  find - 查找进程" -ForegroundColor White
        Write-Host ""
        Write-Host "示例:" -ForegroundColor Yellow
        Write-Host "  .\process-manager.ps1 list -Top 20" -ForegroundColor White
        Write-Host "  .\process-manager.ps1 stopbyname -ProcessName notepad" -ForegroundColor White
        Write-Host "  .\process-manager.ps1 stopbyid -ProcessId 1234" -ForegroundColor White
        Write-Host "  .\process-manager.ps1 find -ProcessName chrome" -ForegroundColor White
    }
}