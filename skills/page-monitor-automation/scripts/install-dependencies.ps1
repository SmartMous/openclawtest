#!/usr/bin/env pwsh
# 安装页面监控与自动化依赖

Write-Host "=== 安装页面监控与自动化依赖 ===" -ForegroundColor Green

# 检查Python
Write-Host "`n1. 检查Python安装..." -ForegroundColor Cyan
$pythonVersion = python --version 2>$null
if ($pythonVersion) {
    Write-Host "  已安装: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  Python未安装，请先安装Python 3.8+" -ForegroundColor Red
    Write-Host "  下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 检查pip
Write-Host "`n2. 检查pip..." -ForegroundColor Cyan
$pipVersion = pip --version 2>$null
if ($pipVersion) {
    Write-Host "  已安装pip" -ForegroundColor Green
} else {
    Write-Host "  安装pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# 安装Python包
Write-Host "`n3. 安装Python依赖包..." -ForegroundColor Cyan
$packages = @(
    "pyautogui",
    "pillow",
    "pytesseract",
    "opencv-python",
    "numpy",
    "pygetwindow",
    "schedule",
    "requests"
)

foreach ($package in $packages) {
    Write-Host "  安装 $package..." -ForegroundColor White -NoNewline
    pip install $package --quiet
    Write-Host " ✓" -ForegroundColor Green
}

# 检查Tesseract OCR
Write-Host "`n4. 检查Tesseract OCR..." -ForegroundColor Cyan
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    Write-Host "  Tesseract已安装" -ForegroundColor Green
} else {
    Write-Host "  Tesseract未安装" -ForegroundColor Yellow
    Write-Host "  请下载安装: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "  安装后需要设置环境变量" -ForegroundColor White
}

# 下载语言包
Write-Host "`n5. 下载OCR语言包..." -ForegroundColor Cyan
$langPacks = @("chi_sim", "eng")
foreach ($lang in $langPacks) {
    $url = "https://github.com/tesseract-ocr/tessdata/raw/main/${lang}.traineddata"
    $output = "$env:TEMP\${lang}.traineddata"
    
    Write-Host "  下载 ${lang}..." -ForegroundColor White -NoNewline
    try {
        Invoke-WebRequest -Uri $url -OutFile $output -ErrorAction Stop
        Write-Host " ✓" -ForegroundColor Green
        
        # 复制到Tesseract目录
        if (Test-Path $tesseractPath) {
            $tessdataDir = "C:\Program Files\Tesseract-OCR\tessdata"
            if (Test-Path $tessdataDir) {
                Copy-Item $output "$tessdataDir\" -Force
                Write-Host "    已复制到Tesseract目录" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host " ✗ (下载失败)" -ForegroundColor Red
    }
}

# 创建示例配置文件
Write-Host "`n6. 创建示例配置..." -ForegroundColor Cyan
$configContent = @'
# 页面监控配置示例
monitoring:
  # 截图设置
  screenshot_quality: 90
  screenshot_format: png
  
  # OCR设置
  ocr_language: chi_sim+eng
  ocr_config: --psm 3 --oem 3
  
  # 图像匹配
  image_match_threshold: 0.8
  match_method: TM_CCOEFF_NORMED
  
  # 监控设置
  check_interval: 60  # 秒
  max_retries: 3
  retry_delay: 2      # 秒

# 任务示例
tasks:
  - name: 网站状态监控
    enabled: true
    type: web_monitor
    url: https://example.com
    schedule: "*/5 * * * *"  # 每5分钟
    
    conditions:
      - type: text
        text: "服务正常"
        operator: contains
        region: [100, 100, 400, 200]  # x, y, width, height
        
      - type: image
        template: "status_ok.png"
        threshold: 0.85
    
    actions:
      - type: log
        message: "网站状态正常"
        
      - type: notification
        title: "监控通知"
        message: "网站运行正常"
    
    failure_actions:
      - type: notification
        title: "警报"
        message: "网站状态异常！"
        
      - type: email
        to: "admin@example.com"
        subject: "网站监控警报"
        body: "检测到网站状态异常"

  - name: 表单自动填写
    enabled: false
    type: form_automation
    schedule: "0 9 * * *"  # 每天9点
    
    conditions:
      - type: image
        template: "login_form.png"
        threshold: 0.9
    
    actions:
      - type: click
        target: "username_field.png"
        
      - type: type
        text: "testuser"
        
      - type: click
        target: "password_field.png"
        
      - type: type
        text: "password123"
        
      - type: click
        target: "submit_button.png"

# 通知设置
notifications:
  email:
    enabled: false
    smtp_server: smtp.example.com
    smtp_port: 587
    username: user@example.com
    password: password
    
  webhook:
    enabled: false
    url: https://hooks.example.com/webhook
    headers:
      Content-Type: application/json
      
  desktop:
    enabled: true
    duration: 5  # 秒

# 日志设置
logging:
  level: INFO
  file: monitor.log
  max_size: 10485760  # 10MB
  backup_count: 5
'@

$configPath = ".\monitor_config.yaml"
$configContent | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "  配置文件已创建: $configPath" -ForegroundColor Green

# 创建基础监控脚本
Write-Host "`n7. 创建基础监控脚本..." -ForegroundColor Cyan
$monitorScript = @'
#!/usr/bin/env python3
# 基础页面监控脚本

import pyautogui
import pytesseract
from PIL import Image
import time
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasicPageMonitor:
    def __init__(self, tesseract_path=None):
        """初始化监控器"""
        # 配置Tesseract路径
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # 尝试默认路径
            default_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            for path in default_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        logger.info("页面监控器初始化完成")
    
    def capture_screen(self, region=None, save_path=None):
        """捕获屏幕截图"""
        try:
            screenshot = pyautogui.screenshot(region=region)
            
            if save_path:
                screenshot.save(save_path)
                logger.debug(f"截图已保存: {save_path}")
            
            return screenshot
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def extract_text(self, image, language='chi_sim+eng'):
        """从图像中提取文字"""
        try:
            text = pytesseract.image_to_string(image, lang=language)
            return text.strip()
        except Exception as e:
            logger.error(f"文字提取失败: {e}")
            return ""
    
    def check_text_presence(self, text_to_find, region=None, language='chi_sim+eng'):
        """检查屏幕上是否包含特定文字"""
        # 截图
        screenshot = self.capture_screen(region=region)
        if not screenshot:
            return False
        
        # 提取文字
        text = self.extract_text(screenshot, language)
        
        # 检查是否包含目标文字
        found = text_to_find in text
        
        if found:
            logger.info(f"找到文字: '{text_to_find}'")
        else:
            logger.debug(f"未找到文字: '{text_to_find}'")
        
        return found
    
    def monitor_with_interval(self, check_function, interval=60, max_checks=None):
        """定时监控"""
        logger.info(f"开始定时监控，间隔: {interval}秒")
        
        check_count = 0
        while True:
            if max_checks and check_count >= max_checks:
                logger.info(f"达到最大检查次数: {max_checks}")
                break
            
            check_count += 1
            logger.debug(f"执行第 {check_count} 次检查")
            
            try:
                result = check_function()
                if result:
                    logger.info("监控条件满足")
                    return True
            except Exception as e:
                logger.error(f"检查失败: {e}")
            
            # 等待下次检查
            time.sleep(interval)
        
        return False

def main():
    """示例使用"""
    monitor = BasicPageMonitor()
    
    # 示例1: 检查屏幕上是否包含"成功"文字
    def check_success():
        return monitor.check_text_presence("成功")
    
    # 示例2: 定时监控
    print("开始监控，按Ctrl+C停止...")
    monitor.monitor_with_interval(check_success, interval=10)

if __name__ == "__main__":
    main()
'@

$scriptPath = ".\basic_monitor.py"
$monitorScript | Out-File -FilePath $scriptPath -Encoding UTF8
Write-Host "  监控脚本已创建: $scriptPath" -ForegroundColor Green

Write-Host "`n=== 安装完成 ===" -ForegroundColor Green
Write-Host "`n下一步:" -ForegroundColor Yellow
Write-Host "1. 确保Tesseract OCR已安装并配置环境变量" -ForegroundColor White
Write-Host "2. 编辑配置文件: $configPath" -ForegroundColor White
Write-Host "3. 运行测试: python $scriptPath" -ForegroundColor White
Write-Host "4. 根据需要创建监控任务" -ForegroundColor White