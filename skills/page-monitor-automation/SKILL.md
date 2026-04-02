---
name: 页面监控与自动化
description: 识别页面中的文字和图像，并根据要求定时完成动作触发。用于监控网页、应用程序界面、屏幕内容，基于识别结果自动执行操作。
---

# 页面监控与自动化技能

用于监控屏幕/页面内容，识别文字和图像，并根据条件定时触发自动化操作。

## 功能概述

### 核心能力
1. **屏幕内容捕获** - 获取屏幕或特定窗口的截图
2. **文字识别(OCR)** - 从图像中提取文字内容
3. **图像识别** - 识别特定图像、图标、按钮等
4. **条件判断** - 基于识别结果进行逻辑判断
5. **动作触发** - 执行鼠标点击、键盘输入等操作
6. **定时调度** - 按计划执行监控任务

## 使用场景

### 常见应用
- 监控网页状态变化并通知
- 自动填写表单或点击按钮
- 监控系统通知并响应
- 自动化测试和验证
- 数据采集和监控
- 定时任务自动化

## 技术架构

### 组件依赖
```
页面监控与自动化
├── 图像捕获 (screenshot/截图)
├── 文字识别 (OCR/Tesseract)
├── 图像识别 (OpenCV/模板匹配)
├── 条件引擎 (规则判断)
├── 动作执行 (自动化操作)
└── 调度器 (定时任务)
```

## 快速开始

### 基础监控示例
```python
# 监控页面是否包含特定文字
from monitor import PageMonitor

monitor = PageMonitor()
result = monitor.check_text_presence(
    url="https://example.com",
    target_text="成功",
    action="notify"
)
```

### 定时任务示例
```python
# 每天9点检查网站状态
from scheduler import TaskScheduler

scheduler = TaskScheduler()
scheduler.add_daily_task(
    time="09:00",
    task=check_website_status,
    args=["https://example.com"]
)
```

## 详细指南

### 1. 屏幕内容捕获

#### 全屏截图
```python
import pyautogui

# 全屏截图
screenshot = pyautogui.screenshot()
screenshot.save('screen.png')

# 指定区域截图
region = (x, y, width, height)
screenshot = pyautogui.screenshot(region=region)
```

#### 窗口截图
```python
import pygetwindow as gw

# 获取特定窗口
window = gw.getWindowsWithTitle('Chrome')[0]

# 激活并截图
window.activate()
screenshot = pyautogui.screenshot(region=window.box)
```

### 2. 文字识别(OCR)

#### 使用Tesseract
```python
import pytesseract
from PIL import Image

# 配置Tesseract路径（Windows）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 识别文字
image = Image.open('screen.png')
text = pytesseract.image_to_string(image, lang='chi_sim+eng')
print(text)
```

#### 特定区域OCR
```python
def extract_text_from_region(image_path, region):
    """从指定区域提取文字"""
    image = Image.open(image_path)
    cropped = image.crop(region)
    text = pytesseract.image_to_string(cropped, lang='chi_sim+eng')
    return text.strip()
```

### 3. 图像识别

#### 模板匹配
```python
import cv2
import numpy as np

def find_template(main_image, template_image, threshold=0.8):
    """在图像中查找模板"""
    main = cv2.imread(main_image)
    template = cv2.imread(template_image)
    
    result = cv2.matchTemplate(main, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    
    return list(zip(*locations[::-1]))
```

#### 特征匹配
```python
def find_image_features(main_image, target_image):
    """使用特征匹配查找图像"""
    # 使用SIFT或ORB特征检测
    # 返回匹配位置和置信度
    pass
```

### 4. 条件判断

#### 文字条件
```python
class TextCondition:
    def __init__(self, text, operator="contains"):
        self.text = text
        self.operator = operator
    
    def check(self, content):
        if self.operator == "contains":
            return self.text in content
        elif self.operator == "equals":
            return content == self.text
        elif self.operator == "starts_with":
            return content.startswith(self.text)
        elif self.operator == "ends_with":
            return content.endswith(self.text)
        return False
```

#### 图像条件
```python
class ImageCondition:
    def __init__(self, template_path, threshold=0.8):
        self.template_path = template_path
        self.threshold = threshold
    
    def check(self, screenshot_path):
        locations = find_template(screenshot_path, self.template_path, self.threshold)
        return len(locations) > 0
```

### 5. 动作触发

#### 鼠标操作
```python
import pyautogui

def click_at_position(x, y):
    """在指定位置点击"""
    pyautogui.moveTo(x, y)
    pyautogui.click()

def click_on_image(template_path):
    """点击找到的图像位置"""
    locations = find_template('current_screen.png', template_path)
    if locations:
        x, y = locations[0]
        click_at_position(x, y)
        return True
    return False
```

#### 键盘操作
```python
def type_text(text):
    """输入文字"""
    pyautogui.typewrite(text)

def press_key(key):
    """按下特定键"""
    pyautogui.press(key)

def hotkey(*keys):
    """组合键"""
    pyautogui.hotkey(*keys)
```

### 6. 完整监控流程

```python
class PageMonitorAutomation:
    def __init__(self):
        self.conditions = []
        self.actions = []
    
    def add_condition(self, condition):
        self.conditions.append(condition)
    
    def add_action(self, action):
        self.actions.append(action)
    
    def run_monitoring(self):
        # 1. 捕获屏幕
        screenshot_path = self.capture_screen()
        
        # 2. 检查所有条件
        conditions_met = True
        for condition in self.conditions:
            if not condition.check(screenshot_path):
                conditions_met = False
                break
        
        # 3. 如果条件满足，执行动作
        if conditions_met:
            for action in self.actions:
                action.execute()
            
            return True
        return False
```

## 定时任务集成

### 使用cron工具
```python
from openclaw.tools import cron

# 创建定时监控任务
job = cron.add_job(
    name="页面监控",
    schedule={"kind": "every", "everyMs": 300000},  # 每5分钟
    payload={
        "kind": "agentTurn",
        "message": "运行页面监控任务"
    }
)
```

### 监控任务配置
```json
{
  "monitor_task": {
    "name": "网站状态监控",
    "url": "https://example.com",
    "check_interval": 300,  # 5分钟
    "conditions": [
      {
        "type": "text",
        "text": "服务正常",
        "operator": "contains"
      }
    ],
    "actions": [
      {
        "type": "notification",
        "message": "网站状态正常"
      }
    ],
    "failure_actions": [
      {
        "type": "notification",
        "message": "网站状态异常！"
      }
    ]
  }
}
```

## 实用示例

### 示例1：监控网页按钮并点击
```python
# 监控网页上的"提交"按钮，出现时自动点击
monitor = PageMonitorAutomation()

# 添加图像条件（查找提交按钮）
button_condition = ImageCondition("submit_button.png", threshold=0.9)
monitor.add_condition(button_condition)

# 添加点击动作
def click_submit():
    click_on_image("submit_button.png")

monitor.add_action(click_submit)

# 定时运行
schedule.every(10).seconds.do(monitor.run_monitoring)
```

### 示例2：监控系统通知
```python
# 监控系统通知区域，发现特定通知时执行操作
def monitor_system_notifications():
    # 截图通知区域
    notification_area = (screen_width-400, 0, 400, 100)
    screenshot = pyautogui.screenshot(region=notification_area)
    screenshot.save('notifications.png')
    
    # OCR识别通知文字
    text = pytesseract.image_to_string('notifications.png', lang='chi_sim')
    
    # 检查是否包含重要通知
    important_keywords = ["错误", "警告", "紧急", "失败"]
    for keyword in important_keywords:
        if keyword in text:
            # 发送警报
            send_alert(f"发现重要通知: {keyword}")
            return True
    
    return False
```

### 示例3：自动化数据录入
```python
# 自动识别表单并填写数据
def automate_form_filling():
    # 1. 定位表单字段
    name_field = find_template('current_screen.png', 'name_field.png')
    email_field = find_template('current_screen.png', 'email_field.png')
    submit_button = find_template('current_screen.png', 'submit_button.png')
    
    if name_field and email_field and submit_button:
        # 2. 点击并填写字段
        click_at_position(*name_field[0])
        type_text("张三")
        
        click_at_position(*email_field[0])
        type_text("zhangsan@example.com")
        
        # 3. 提交表单
        click_at_position(*submit_button[0])
        return True
    
    return False
```

## 配置说明

### 安装依赖
```bash
# Python依赖
pip install pyautogui pillow pytesseract opencv-python numpy pygetwindow

# Tesseract OCR (Windows)
# 下载地址: https://github.com/UB-Mannheim/tesseract/wiki
# 安装后设置环境变量
```

### 配置文件
```yaml
# config.yaml
monitoring:
  screenshot_quality: 90
  ocr_language: chi_sim+eng
  image_match_threshold: 0.8
  check_interval: 60  # 秒
  
tasks:
  - name: 网站监控
    enabled: true
    schedule: "*/5 * * * *"  # 每5分钟
    url: "https://example.com"
    conditions: [...]
    actions: [...]
```

## 故障排除

### 常见问题

#### 1. OCR识别率低
- 调整图像对比度和亮度
- 使用更高分辨率的截图
- 训练自定义OCR模型
- 指定正确的语言包

#### 2. 图像匹配失败
- 调整匹配阈值
- 使用多种匹配方法
- 考虑光照和颜色变化
- 使用特征匹配代替模板匹配

#### 3. 自动化操作失败
- 添加适当的延迟
- 验证元素位置
- 使用相对坐标
- 添加重试机制

#### 4. 定时任务不执行
- 检查cron服务状态
- 验证任务配置
- 检查权限设置
- 查看日志文件

### 调试技巧
```python
# 启用调试模式
import logging
logging.basicConfig(level=logging.DEBUG)

# 保存中间结果
def debug_save(image, name):
    image.save(f'debug_{name}.png')
    print(f"已保存调试图像: debug_{name}.png")

# 添加超时和重试
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
```

## 安全注意事项

1. **权限管理** - 仅授予必要的系统权限
2. **数据保护** - 不存储敏感信息
3. **操作确认** - 重要操作前请求确认
4. **速率限制** - 避免过快操作触发防护
5. **错误处理** - 妥善处理异常情况
6. **日志记录** - 记录所有自动化操作

## 性能优化

### 优化建议
1. **区域监控** - 只监控特定区域而非全屏
2. **缓存结果** - 缓存不变的界面元素
3. **并行处理** - 同时监控多个条件
4. **智能调度** - 根据历史数据调整检查频率
5. **资源管理** - 及时释放图像内存

### 内存管理
```python
import gc

def monitor_with_cleanup():
    try:
        # 执行监控
        result = perform_monitoring()
        return result
    finally:
        # 清理资源
        gc.collect()
```

---

**注意**: 本技能需要适当的系统权限和依赖安装。在生产环境使用前，请在测试环境充分验证。