#!/usr/bin/env pwsh
# Windows 临时文件清理脚本

Write-Host "=== Windows 临时文件清理 ===" -ForegroundColor Green

# 清理前的磁盘空间
$before = Get-PSDrive C | Select-Object Used, Free
$beforeUsed = [math]::Round($before.Used / 1GB, 2)
$beforeFree = [math]::Round($before.Free / 1GB, 2)

Write-Host "清理前磁盘空间:" -ForegroundColor Yellow
Write-Host "  已使用: ${beforeUsed} GB" -ForegroundColor White
Write-Host "  可用空间: ${beforeFree} GB" -ForegroundColor White

# 要清理的目录列表
$tempDirs = @(
    "$env:TEMP",
    "C:\Windows\Temp",
    "$env:LOCALAPPDATA\Temp",
    "$env:USERPROFILE\AppData\Local\Temp",
    "$env:USERPROFILE\AppData\Local\Microsoft\Windows\INetCache",
    "$env:USERPROFILE\AppData\Local\Microsoft\Windows\INetCookies",
    "$env:USERPROFILE\AppData\Local\Microsoft\Windows\History"
)

$totalCleaned = 0
$cleanedFiles = 0
$cleanedDirs = 0

foreach ($dir in $tempDirs) {
    if (Test-Path $dir) {
        Write-Host "`n清理目录: $dir" -ForegroundColor Cyan
        
        try {
            # 获取目录中的文件和文件夹
            $items = Get-ChildItem -Path $dir -Recurse -ErrorAction SilentlyContinue
            
            if ($items) {
                $dirSize = ($items | Measure-Object Length -Sum).Sum
                $dirSizeMB = [math]::Round($dirSize / 1MB, 2)
                
                Write-Host "  找到 ${dirSizeMB} MB 数据" -ForegroundColor White
                
                # 尝试删除文件
                $files = Get-ChildItem -Path $dir -File -Recurse -ErrorAction SilentlyContinue
                foreach ($file in $files) {
                    try {
                        Remove-Item -Path $file.FullName -Force -ErrorAction Stop
                        $cleanedFiles++
                    } catch {
                        Write-Host "  无法删除: $($file.Name)" -ForegroundColor DarkGray
                    }
                }
                
                # 尝试删除空文件夹
                $emptyDirs = Get-ChildItem -Path $dir -Directory -Recurse -ErrorAction SilentlyContinue | 
                    Where-Object { (Get-ChildItem -Path $_.FullName -Recurse -ErrorAction SilentlyContinue).Count -eq 0 }
                
                foreach ($emptyDir in $emptyDirs) {
                    try {
                        Remove-Item -Path $emptyDir.FullName -Force -Recurse -ErrorAction Stop
                        $cleanedDirs++
                    } catch {
                        # 忽略删除失败的空文件夹
                    }
                }
                
                $totalCleaned += $dirSize
            } else {
                Write-Host "  目录为空" -ForegroundColor DarkGray
            }
        } catch {
            Write-Host "  访问目录失败" -ForegroundColor Red
        }
    } else {
        Write-Host "`n目录不存在: $dir" -ForegroundColor DarkGray
    }
}

# 清理回收站
Write-Host "`n清空回收站..." -ForegroundColor Cyan
Clear-RecycleBin -Force -ErrorAction SilentlyContinue

# 清理后的磁盘空间
$after = Get-PSDrive C | Select-Object Used, Free
$afterUsed = [math]::Round($after.Used / 1GB, 2)
$afterFree = [math]::Round($after.Free / 1GB, 2)

$cleanedGB = [math]::Round(($beforeUsed - $afterUsed), 2)

Write-Host "`n=== 清理结果 ===" -ForegroundColor Green
Write-Host "清理文件数: ${cleanedFiles}" -ForegroundColor White
Write-Host "清理文件夹数: ${cleanedDirs}" -ForegroundColor White
Write-Host "释放空间: ${cleanedGB} GB" -ForegroundColor White
Write-Host ""
Write-Host "清理后磁盘空间:" -ForegroundColor Yellow
Write-Host "  已使用: ${afterUsed} GB" -ForegroundColor White
Write-Host "  可用空间: ${afterFree} GB" -ForegroundColor White

# 建议
Write-Host "`n=== 建议 ===" -ForegroundColor Yellow
Write-Host "1. 运行磁盘清理工具: cleanmgr" -ForegroundColor White
Write-Host "2. 清理系统更新文件: DISM /Online /Cleanup-Image /StartComponentCleanup" -ForegroundColor White
Write-Host "3. 清理Windows更新缓存: net stop wuauserv & del /q C:\Windows\SoftwareDistribution\Download\* & net start wuauserv" -ForegroundColor White

Write-Host "`n=== 清理完成 ===" -ForegroundColor Green