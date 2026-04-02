---
name: Windows控制
description: Windows系统控制和管理技能。用于文件管理、进程控制、系统信息查询、网络配置、服务管理等Windows系统操作。
---

# Windows 控制技能

用于管理和控制Windows系统的技能。

## 常用命令

### 文件管理
```powershell
# 列出文件
Get-ChildItem
dir
ls

# 复制文件
Copy-Item source destination
copy source destination

# 移动文件
Move-Item source destination
move source destination

# 删除文件
Remove-Item path
del path
rm path

# 创建目录
New-Item -ItemType Directory -Path path
mkdir path
```

### 进程管理
```powershell
# 列出进程
Get-Process
tasklist

# 结束进程
Stop-Process -Name processname
taskkill /IM processname.exe /F

# 按ID结束进程
Stop-Process -Id pid
taskkill /PID pid /F
```

### 系统信息
```powershell
# 系统信息
systeminfo

# 磁盘信息
Get-PSDrive
wmic logicaldisk get size,freespace,caption

# 内存信息
Get-WmiObject Win32_OperatingSystem | Select TotalVisibleMemorySize,FreePhysicalMemory
```

### 网络配置
```powershell
# IP配置
ipconfig /all

# 网络连接
netstat -ano

# 路由表
route print

# DNS缓存
ipconfig /displaydns
```

### 服务管理
```powershell
# 列出服务
Get-Service
sc query

# 启动服务
Start-Service servicename
sc start servicename

# 停止服务
Stop-Service servicename
sc stop servicename

# 服务状态
Get-Service servicename | Select Status
```

### 用户管理
```powershell
# 当前用户
whoami

# 用户信息
net user

# 组信息
net localgroup
```

### 计划任务
```powershell
# 列出任务
Get-ScheduledTask

# 任务详情
Get-ScheduledTask -TaskName taskname | Get-ScheduledTaskInfo

# 运行任务
Start-ScheduledTask -TaskName taskname
```

### 注册表操作
```powershell
# 读取注册表
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion"

# 写入注册表
Set-ItemProperty -Path "HKCU:\Software\Test" -Name "ValueName" -Value "Value"

# 删除注册表
Remove-ItemProperty -Path "HKCU:\Software\Test" -Name "ValueName"
```

### 电源管理
```powershell
# 关机
shutdown /s /t 0

# 重启
shutdown /r /t 0

# 休眠
rundll32.exe powrprof.dll,SetSuspendState 0,1,0

# 睡眠
powercfg -h off
```

### 事件查看器
```powershell
# 系统日志
Get-EventLog -LogName System -Newest 10

# 应用日志
Get-EventLog -LogName Application -Newest 10

# 安全日志
Get-EventLog -LogName Security -Newest 10
```

## 实用脚本

### 清理临时文件
```powershell
# 清理Windows临时文件
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# 清理用户临时文件
Remove-Item -Path "$env:LOCALAPPDATA\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
```

### 磁盘清理
```powershell
# 磁盘清理工具
cleanmgr /sageset:1
cleanmgr /sagerun:1
```

### 系统健康检查
```powershell
# 检查磁盘错误
chkdsk C: /f

# 系统文件检查
sfc /scannow

# DISM修复
DISM /Online /Cleanup-Image /RestoreHealth
```

## 安全提示

1. **谨慎使用管理员权限** - 某些命令需要管理员权限
2. **备份重要数据** - 在执行删除或修改操作前备份
3. **了解命令作用** - 不要运行不理解的命令
4. **使用-WhatIf参数** - 在PowerShell中，使用-WhatIf查看命令效果而不执行

## 故障排除

### 权限问题
```powershell
# 以管理员运行PowerShell
Start-Process powershell -Verb RunAs
```

### 命令找不到
```powershell
# 检查命令是否存在
Get-Command commandname -ErrorAction SilentlyContinue

# 添加路径
$env:Path += ";C:\Path\To\Tool"
```

### 脚本执行策略
```powershell
# 查看当前策略
Get-ExecutionPolicy

# 设置策略（谨慎使用）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 最佳实践

1. **使用PowerShell代替CMD** - PowerShell更强大且面向对象
2. **使用别名提高效率** - 如`ls`代替`Get-ChildItem`
3. **利用管道** - 如`Get-Process | Where CPU -gt 10`
4. **记录操作** - 使用`Start-Transcript`记录会话
5. **测试命令** - 在生产环境前在测试环境验证

---

**注意**: 本技能提供Windows系统管理的基础知识。对于高级操作，请参考Microsoft官方文档或咨询系统管理员。