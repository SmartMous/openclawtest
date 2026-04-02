# Windows 控制快速参考

## 常用命令速查

### 系统信息
```powershell
# 基本系统信息
systeminfo
hostname
ver

# 详细系统信息
Get-ComputerInfo
Get-WmiObject Win32_OperatingSystem | Select Caption,Version,OSArchitecture

# 硬件信息
wmic cpu get name,NumberOfCores,NumberOfLogicalProcessors
wmic memorychip get capacity
wmic diskdrive get size,model
```

### 文件操作
```powershell
# 导航
cd [路径]
pwd

# 列表
dir
ls
Get-ChildItem

# 创建
mkdir 目录名
New-Item 文件名 -ItemType File
New-Item 目录名 -ItemType Directory

# 复制/移动
copy 源 目标
xcopy 源 目标 /E /I /H
move 源 目标
robocopy 源 目标 /MIR

# 删除
del 文件
rm 文件
Remove-Item 路径 -Recurse -Force
```

### 进程管理
```powershell
# 查看进程
tasklist
Get-Process
ps

# 结束进程
taskkill /IM 进程名.exe /F
taskkill /PID 进程ID /F
Stop-Process -Name 进程名 -Force
Stop-Process -Id 进程ID -Force

# 按条件查找
Get-Process | Where {$_.CPU -gt 10}
Get-Process | Sort-Object CPU -Descending | Select -First 10
```

### 服务管理
```powershell
# 查看服务
sc query
Get-Service
services.msc

# 控制服务
sc start 服务名
sc stop 服务名
sc pause 服务名
sc continue 服务名

# PowerShell方式
Start-Service 服务名
Stop-Service 服务名
Restart-Service 服务名
```

### 网络管理
```powershell
# IP配置
ipconfig /all
ipconfig /release
ipconfig /renew

# 网络诊断
ping 地址
tracert 地址
pathping 地址
nslookup 域名

# 连接查看
netstat -ano
netstat -an | find "ESTABLISHED"
Get-NetTCPConnection

# 防火墙
netsh advfirewall show allprofiles
netsh advfirewall set allprofiles state off
netsh advfirewall set allprofiles state on
```

### 用户和权限
```powershell
# 用户信息
whoami
whoami /all
net user
net user 用户名

# 组信息
net localgroup
net localgroup administrators

# 权限检查
icacls 文件或目录
takeown /f 文件 /a
cacls 文件 /e /p 用户权限
```

### 注册表操作
```powershell
# 导航
reg query 路径
reg add 路径 /v 值名 /t 类型 /d 数据
reg delete 路径 /v 值名 /f
reg export 路径 文件名.reg
reg import 文件名.reg

# 常用路径
HKEY_LOCAL_MACHINE\SOFTWARE
HKEY_CURRENT_USER\Software
HKEY_CLASSES_ROOT
```

### 计划任务
```powershell
# 查看任务
schtasks /query
schtasks /query /tn 任务名

# 创建任务
schtasks /create /tn 任务名 /tr 程序 /sc 计划

# 运行任务
schtasks /run /tn 任务名

# 删除任务
schtasks /delete /tn 任务名 /f
```

### 事件日志
```powershell
# 查看日志
eventvwr.msc
Get-EventLog -LogName System -Newest 20
Get-EventLog -LogName Application -Newest 20
Get-EventLog -LogName Security -Newest 20

# 筛选日志
Get-EventLog -LogName System -EntryType Error
Get-EventLog -LogName Application | Where {$_.Source -eq "Application Error"}
```

### 磁盘管理
```powershell
# 磁盘信息
wmic logicaldisk get size,freespace,caption
Get-PSDrive
fsutil fsinfo drives

# 磁盘检查
chkdsk C: /f
chkdsk C: /r

# 清理
cleanmgr
diskpart
defrag C: /U /V
```

### 电源管理
```powershell
# 关机/重启
shutdown /s /t 0
shutdown /r /t 0
shutdown /l
shutdown /h

# 电源设置
powercfg /list
powercfg /query
powercfg /h off
```

## 实用单行命令

### 系统维护
```powershell
# 清理临时文件
Remove-Item $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue

# 清理DNS缓存
ipconfig /flushdns

# 重置网络
netsh winsock reset

# 修复系统文件
sfc /scannow
DISM /Online /Cleanup-Image /RestoreHealth
```

### 监控
```powershell
# 实时进程监控
Get-Process | Sort-Object CPU -Descending | Select -First 5

# 磁盘空间监控
Get-PSDrive -PSProvider FileSystem | Select Name,Used,Free

# 网络连接监控
netstat -an | find "ESTABLISHED"

# 服务状态监控
Get-Service | Where {$_.Status -ne "Running"}
```

### 信息收集
```powershell
# 收集系统信息到文件
systeminfo > systeminfo.txt
ipconfig /all > network.txt
tasklist > processes.txt
Get-Service > services.txt
```

## 故障排除流程

### 1. 系统慢
```powershell
# 检查CPU使用
Get-Process | Sort-Object CPU -Descending | Select -First 10

# 检查内存使用
Get-Process | Sort-Object WorkingSet -Descending | Select -First 10

# 检查磁盘活动
Get-Counter "\PhysicalDisk(*)\% Disk Time"

# 检查网络
netstat -ano | find "ESTABLISHED"
```

### 2. 无法启动程序
```powershell
# 检查依赖
where 程序名
Get-Command 程序名

# 检查权限
whoami /priv

# 检查事件日志
Get-EventLog -LogName Application -Newest 20 | Where {$_.Source -like "*程序名*"}
```

### 3. 网络问题
```powershell
# 基本连接
ping 8.8.8.8
ping google.com

# DNS解析
nslookup google.com
Resolve-DnsName google.com

# 路由跟踪
tracert google.com
Test-NetConnection google.com -TraceRoute

# 端口检查
Test-NetConnection google.com -Port 443
```

## 安全最佳实践

1. **最小权限原则** - 不要使用管理员账户进行日常操作
2. **定期更新** - 保持系统和软件更新
3. **备份重要数据** - 定期备份关键文件
4. **使用防病毒软件** - 保持实时保护
5. **谨慎运行脚本** - 只运行可信来源的脚本
6. **监控系统日志** - 定期检查异常活动
7. **使用强密码** - 启用密码复杂性要求
8. **禁用不必要的服务** - 减少攻击面

## 紧急情况处理

### 系统无法启动
1. 尝试安全模式 (F8)
2. 使用系统还原
3. 使用启动修复
4. 使用安装媒体修复

### 病毒/恶意软件
1. 断开网络
2. 进入安全模式
3. 运行防病毒扫描
4. 使用恶意软件清除工具

### 数据丢失
1. 立即停止使用受影响磁盘
2. 使用数据恢复软件
3. 从备份恢复
4. 寻求专业帮助

---

**注意**: 本参考文档适用于Windows 10/11系统。某些命令可能需要管理员权限。在执行可能影响系统的命令前，请确保了解其作用。