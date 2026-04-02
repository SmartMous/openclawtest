#!/usr/bin/env python3
"""
简单页面监控脚本
功能：监控屏幕上的文字和图像，根据条件触发动作
"""

import pyautogui
import pytesseract
from PIL import Image
import time
import logging
import os
import sys
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimplePageMonitor:
    def __init__(self, config_file=None):
        """初始化监控器"""
        self.config = self.load_config(config_file)
        self.setup_tesseract()
        logger.info("页面监控器初始化完成")
    
    def load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            'tesseract_path': None,
            'language': 'chi_sim+eng',
            'screenshot_dir': 'screenshots',
            'check_interval': 60,
            'monitor_regions': {},
            'conditions': [],
            'actions': []
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"已加载配置文件: {config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
        
        return default_config
    
    def setup_tesseract(self):
        """设置Tesseract OCR路径"""
        tesseract_path = self.config.get('tesseract_path')
        
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"使用Tesseract路径: {tesseract_path}")
        else:
            # 尝试常见路径
            default_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract'
            ]
            
            for path in default_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"自动找到Tesseract: {path}")
                    break
            else:
                logger.warning("未找到Tesseract，OCR功能可能无法使用")
    
    def capture_screen(self, region=None, save=True):
        """捕获屏幕截图"""
        try:
            # 创建截图目录
            screenshot_dir = self.config.get('screenshot_dir', 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # 截图
            screenshot = pyautogui.screenshot(region=region)
            
            if save:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{screenshot_dir}/screenshot_{timestamp}.png"
                screenshot.save(filename)
                logger.debug(f"截图已保存: {filename}")
            
            return screenshot
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def extract_text(self, image, language=None):
        """从图像中提取文字"""
        if language is None:
            language = self.config.get('language', 'chi_sim+eng')
        
        try:
            text = pytesseract.image_to_string(image, lang=language)
            return text.strip()
        except Exception as e:
            logger.error(f"文字提取失败: {e}")
            return ""
    
    def check_text_condition(self, condition):
        """检查文字条件"""
        text_to_find = condition.get('text', '')
        region = condition.get('region')  # (x, y, width, height)
        operator = condition.get('operator', 'contains')
        
        if not text_to_find:
            logger.warning("文字条件未指定要查找的文字")
            return False
        
        # 截图
        screenshot = self.capture_screen(region=region, save=False)
        if not screenshot:
            return False
        
        # 提取文字
        extracted_text = self.extract_text(screenshot)
        
        # 根据操作符检查
        if operator == 'contains':
            result = text_to_find in extracted_text
        elif operator == 'equals':
            result = extracted_text == text_to_find
        elif operator == 'starts_with':
            result = extracted_text.startswith(text_to_find)
        elif operator == 'ends_with':
            result = extracted_text.endswith(text_to_find)
        elif operator == 'not_contains':
            result = text_to_find not in extracted_text
        else:
            logger.warning(f"未知的操作符: {operator}")
            return False
        
        if result:
            logger.info(f"文字条件满足: 找到 '{text_to_find}' (操作符: {operator})")
        else:
            logger.debug(f"文字条件不满足: 未找到 '{text_to_find}'")
        
        return result
    
    def execute_action(self, action):
        """执行动作"""
        action_type = action.get('type', '')
        
        logger.info(f"执行动作: {action_type}")
        
        try:
            if action_type == 'click':
                # 点击动作
                x = action.get('x')
                y = action.get('y')
                if x is not None and y is not None:
                    pyautogui.click(x, y)
                    logger.info(f"点击位置: ({x}, {y})")
            
            elif action_type == 'type':
                # 输入文字
                text = action.get('text', '')
                if text:
                    pyautogui.typewrite(text)
                    logger.info(f"输入文字: {text}")
            
            elif action_type == 'press':
                # 按键
                key = action.get('key', '')
                if key:
                    pyautogui.press(key)
                    logger.info(f"按键: {key}")
            
            elif action_type == 'hotkey':
                # 组合键
                keys = action.get('keys', [])
                if keys:
                    pyautogui.hotkey(*keys)
                    logger.info(f"组合键: {keys}")
            
            elif action_type == 'wait':
                # 等待
                seconds = action.get('seconds', 1)
                time.sleep(seconds)
                logger.info(f"等待 {seconds} 秒")
            
            elif action_type == 'log':
                # 日志记录
                message = action.get('message', '')
                logger.info(f"动作日志: {message}")
            
            elif action_type == 'notification':
                # 显示通知
                title = action.get('title', '监控通知')
                message = action.get('message', '')
                duration = action.get('duration', 5)
                
                # 使用系统通知
                try:
                    import win10toast
                    toast = win10toast.ToastNotifier()
                    toast.show_toast(title, message, duration=duration)
                    logger.info(f"显示通知: {title} - {message}")
                except ImportError:
                    logger.warning("win10toast未安装，无法显示通知")
            
            else:
                logger.warning(f"未知的动作类型: {action_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"执行动作失败: {e}")
            return False
    
    def run_monitoring_cycle(self):
        """运行一次监控周期"""
        logger.info("开始监控周期")
        
        # 检查所有条件
        conditions = self.config.get('conditions', [])
        all_conditions_met = True
        
        for i, condition in enumerate(conditions):
            condition_type = condition.get('type', '')
            
            if condition_type == 'text':
                condition_met = self.check_text_condition(condition)
            else:
                logger.warning(f"未知的条件类型: {condition_type}")
                condition_met = False
            
            if not condition_met:
                all_conditions_met = False
                logger.info(f"条件 {i+1} 未满足")
                break
        
        # 如果所有条件都满足，执行动作
        if all_conditions_met:
            logger.info("所有条件满足，开始执行动作")
            
            actions = self.config.get('actions', [])
            for i, action in enumerate(actions):
                success = self.execute_action(action)
                if not success:
                    logger.warning(f"动作 {i+1} 执行失败")
            
            return True
        else:
            logger.info("条件未全部满足，不执行动作")
            return False
    
    def start_monitoring(self, interval=None, max_cycles=None):
        """开始持续监控"""
        if interval is None:
            interval = self.config.get('check_interval', 60)
        
        logger.info(f"开始持续监控，检查间隔: {interval}秒")
        
        cycle_count = 0
        try:
            while True:
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"达到最大监控周期: {max_cycles}")
                    break
                
                cycle_count += 1
                logger.info(f"=== 第 {cycle_count} 次监控周期 ===")
                
                self.run_monitoring_cycle()
                
                # 等待下次检查
                logger.info(f"等待 {interval} 秒后进行下次检查...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("监控被用户中断")
        except Exception as e:
            logger.error(f"监控过程中发生错误: {e}")
        
        logger.info("监控结束")

def create_example_config():
    """创建示例配置文件"""
    example_config = {
        "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        "language": "chi_sim+eng",
        "screenshot_dir": "monitor_screenshots",
        "check_interval": 30,
        
        "conditions": [
            {
                "type": "text",
                "text": "成功",
                "operator": "contains",
                "region": [100, 100, 400, 200]  # 监控区域
            }
        ],
        
        "actions": [
            {
                "type": "log",
                "message": "检测到'成功'文字"
            },
            {
                "type": "notification",
                "title": "监控通知",
                "message": "检测到目标文字：成功",
                "duration": 5
            },
            {
                "type": "click",
                "x": 500,
                "y": 300
            }
        ]
    }
    
    return example_config

def main():
    """主函数"""
    print("=== 简单页面监控工具 ===")
    print("功能：监控屏幕文字，根据条件触发动作")
    print()
    
    # 检查参数
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = 'monitor_config.json'
        
        # 如果配置文件不存在，创建示例配置
        if not os.path.exists(config_file):
            print(f"配置文件 {config_file} 不存在，创建示例配置...")
            example_config = create_example_config()
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(example_config, f, ensure_ascii=False, indent=2)
            print(f"示例配置文件已创建: {config_file}")
            print("请编辑此文件以配置监控条件")
    
    # 创建监控器
    try:
        monitor = SimplePageMonitor(config_file)
    except Exception as e:
        print(f"初始化监控器失败: {e}")
        print("请检查Tesseract OCR是否安装")
        return
    
    # 开始监控
    print("开始监控，按Ctrl+C停止...")
    print(f"检查间隔: {monitor.config.get('check_interval', 60)}秒")
    print()
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("监控已停止")
    except Exception as e:
        print(f"监控过程中出错: {e}")

if __name__ == "__main__":
    main()