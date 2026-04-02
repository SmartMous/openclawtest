#!/usr/bin/env pwsh
# Windows 系统信息脚本

Write-Host "=== Windows 系统信息 ===" -ForegroundColor Green

# 操作系统信息
$os = Get-WmiObject Win32_OperatingSystem
Write-Host "操作系统: $($os.Caption)" -ForegroundColor Cyan
Write-Host "版本: $($os.Version)" -ForegroundColor Cyan
Write-Host "架构: $($os.OSArchitecture)" -ForegroundColor Cyan
Write-Host "安装日期: $($os.InstallDate)" -ForegroundColor Cyan

# 计算机信息
$computer = Get-WmiObject Win32_ComputerSystem
Write-Host "`n计算机名称: $($computer.Name)" -ForegroundColor Yellow
Write-Host "制造商: $($computer.Manufacturer)" -ForegroundColor Yellow
Write-Host "型号: $($computer.Model)" -ForegroundColor Yellow

# 处理器信息
$cpu = Get-WmiObject Win32_Processor
Write-Host "`n处理器: $($cpu.Name)" -ForegroundColor Magenta
Write-Host "核心数: $($cpu.NumberOfCores)" -ForegroundColor Magenta
Write-Host "逻辑处理器: $($cpu.NumberOfLogicalProcessors)" -ForegroundColor Magenta

# 内存信息
$totalMemory = [math]::Round($computer.TotalPhysicalMemory / 1GB, 2)
$osMemory = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeMemory = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
Write-Host "`n物理内存: ${totalMemory} GB" -ForegroundColor Green
Write-Host "可用内存: ${freeMemory} MB / ${osMemory} MB" -ForegroundColor Green

# 磁盘信息
Write-Host "`n=== 磁盘信息 ===" -ForegroundColor Green
Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $size = [math]::Round($_.Size / 1GB, 2)
    $free = [math]::Round($_.FreeSpace / 1GB, 2)
    $used = $size - $free
    $percent = [math]::Round(($used / $size) * 100, 2)
    
    Write-Host "磁盘 $($_.DeviceID):" -ForegroundColor Cyan
    Write-Host "  总大小: ${size} GB" -ForegroundColor White
    Write-Host "  已使用: ${used} GB (${percent}%)" -ForegroundColor White
    Write-Host "  可用空间: ${free} GB" -ForegroundColor White
}

# 网络适配器
Write-Host "`n=== 网络适配器 ===" -ForegroundColor Green
Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled=True" | ForEach-Object {
    Write-Host "适配器: $($_.Description)" -ForegroundColor Cyan
    Write-Host "  IP地址: $($_.IPAddress -join ', ')" -ForegroundColor White
    Write-Host "  MAC地址: $($_.MACAddress)" -ForegroundColor White
    Write-Host "  DNS: $($_.DNSServerSearchOrder -join ', ')" -ForegroundColor White
}

# 运行时间
$uptime = (Get-Date) - $os.ConvertToDateTime($os.LastBootUpTime)
Write-Host "`n系统运行时间: $($uptime.Days)天 $($uptime.Hours)小时 $($uptime.Minutes)分钟" -ForegroundColor Yellow

Write-Host "`n=== 信息收集完成 ===" -ForegroundColor Green