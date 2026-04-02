#!/usr/bin/env python3
"""
定时任务调度器
将页面监控任务集成到OpenClaw的cron系统中
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitorScheduler:
    def __init__(self, config_dir='.'):
        """初始化调度器"""
        self.config_dir = config_dir
        self.tasks_file = os.path.join(config_dir, 'scheduled_tasks.json')
        self.load_tasks()
    
    def load_tasks(self):
        """加载任务配置"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                logger.info(f"已加载任务配置: {self.tasks_file}")
            except Exception as e:
                logger.error(f"加载任务配置失败: {e}")
                self.tasks = {}
        else:
            self.tasks = {}
            logger.info("任务配置文件不存在，创建空配置")
    
    def save_tasks(self):
        """保存任务配置"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            logger.info(f"任务配置已保存: {self.tasks_file}")
        except Exception as e:
            logger.error(f"保存任务配置失败: {e}")
    
    def add_task(self, task_id, task_config):
        """添加任务"""
        self.tasks[task_id] = task_config
        self.save_tasks()
        logger.info(f"已添加任务: {task_id}")
    
    def remove_task(self, task_id):
        """移除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            logger.info(f"已移除任务: {task_id}")
            return True
        else:
            logger.warning(f"任务不存在: {task_id}")
            return False
    
    def list_tasks(self):
        """列出所有任务"""
        if not self.tasks:
            print("当前没有定时任务")
            return
        
        print("=== 当前定时任务 ===")
        for task_id, config in self.tasks.items():
            print(f"\n任务ID: {task_id}")
            print(f"  名称: {config.get('name', '未命名')}")
            print(f"  启用: {config.get('enabled', False)}")
            print(f"  类型: {config.get('type', 'unknown')}")
            print(f"  计划: {config.get('schedule', '未设置')}")
            print(f"  最后运行: {config.get('last_run', '从未运行')}")
    
    def create_cron_job(self, task_id, task_config):
        """创建OpenClaw cron任务"""
        # 这里需要根据OpenClaw的cron API创建任务
        # 由于cron工具需要直接调用，这里提供生成命令的示例
        
        schedule = task_config.get('schedule', {})
        monitor_config = task_config.get('monitor_config', {})
        
        # 生成cron命令
        cron_command = self.generate_cron_command(task_id, schedule, monitor_config)
        
        return cron_command
    
    def generate_cron_command(self, task_id, schedule, monitor_config):
        """生成cron命令"""
        # 根据schedule类型生成不同的cron表达式
        schedule_type = schedule.get('type', 'interval')
        
        if schedule_type == 'interval':
            # 间隔执行
            interval_seconds = schedule.get('interval', 300)
            cron_expr = self.interval_to_cron(interval_seconds)
        elif schedule_type == 'daily':
            # 每天固定时间
            time_str = schedule.get('time', '09:00')
            hour, minute = map(int, time_str.split(':'))
            cron_expr = f"{minute} {hour} * * *"
        elif schedule_type == 'weekly':
            # 每周特定时间
            time_str = schedule.get('time', '09:00')
            day_of_week = schedule.get('day', 1)  # 1=周一
            hour, minute = map(int, time_str.split(':'))
            cron_expr = f"{minute} {hour} * * {day_of_week}"
        elif schedule_type == 'cron':
            # 直接使用cron表达式
            cron_expr = schedule.get('expression', '* * * * *')
        else:
            logger.error(f"未知的计划类型: {schedule_type}")
            return None
        
        # 构建监控命令
        monitor_script = monitor_config.get('script', 'simple-monitor.py')
        config_file = monitor_config.get('config', f'{task_id}_config.json')
        
        command = f"python {monitor_script} {config_file}"
        
        # 完整的cron任务配置
        cron_job = {
            "name": f"页面监控-{task_id}",
            "schedule": {
                "kind": "cron",
                "expr": cron_expr,
                "tz": "Asia/Shanghai"
            },
            "payload": {
                "kind": "systemEvent",
                "text": f"执行页面监控任务: {task_id}"
            },
            "sessionTarget": "main",
            "enabled": True
        }
        
        return cron_job
    
    def interval_to_cron(self, interval_seconds):
        """将间隔秒数转换为cron表达式"""
        if interval_seconds >= 86400:  # 24小时
            days = interval_seconds // 86400
            return f"0 0 */{days} * *"
        elif interval_seconds >= 3600:  # 1小时
            hours = interval_seconds // 3600
            return f"0 */{hours} * * *"
        elif interval_seconds >= 60:  # 1分钟
            minutes = interval_seconds // 60
            return f"*/{minutes} * * * *"
        else:
            # 小于1分钟，使用每分钟执行
            return "* * * * *"
    
    def run_task_now(self, task_id):
        """立即运行任务"""
        if task_id not in self.tasks:
            logger.error(f"任务不存在: {task_id}")
            return False
        
        task_config = self.tasks[task_id]
        monitor_config = task_config.get('monitor_config', {})
        
        # 获取监控脚本和配置
        monitor_script = monitor_config.get('script', 'simple-monitor.py')
        config_file = monitor_config.get('config', f'{task_id}_config.json')
        
        # 检查文件是否存在
        if not os.path.exists(monitor_script):
            logger.error(f"监控脚本不存在: {monitor_script}")
            return False
        
        if not os.path.exists(config_file):
            logger.error(f"配置文件不存在: {config_file}")
            return False
        
        # 运行监控脚本
        try:
            logger.info(f"开始运行任务: {task_id}")
            
            # 使用subprocess运行脚本
            result = subprocess.run(
                [sys.executable, monitor_script, config_file],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 更新最后运行时间
            task_config['last_run'] = datetime.now().isoformat()
            self.tasks[task_id] = task_config
            self.save_tasks()
            
            if result.returncode == 0:
                logger.info(f"任务执行成功: {task_id}")
                logger.debug(f"输出: {result.stdout}")
                return True
            else:
                logger.error(f"任务执行失败: {task_id}")
                logger.error(f"错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"任务执行超时: {task_id}")
            return False
        except Exception as e:
            logger.error(f"运行任务时出错: {e}")
            return False

def create_example_task():
    """创建示例任务配置"""
    example_task = {
        "website_monitor": {
            "name": "网站状态监控",
            "enabled": True,
            "type": "web_monitor",
            "schedule": {
                "type": "interval",
                "interval": 300  # 5分钟
            },
            "monitor_config": {
                "script": "simple-monitor.py",
                "config": "website_config.json"
            },
            "description": "监控网站是否包含'服务正常'文字",
            "last_run": None
        },
        "daily_check": {
            "name": "每日检查",
            "enabled": True,
            "type": "daily_check",
            "schedule": {
                "type": "daily",
                "time": "09:00"  # 每天9点
            },
            "monitor_config": {
                "script": "simple-monitor.py",
                "config": "daily_config.json"
            },
            "description": "每天检查系统状态",
            "last_run": None
        }
    }
    
    return example_task

def main():
    """主函数"""
    print("=== 页面监控定时任务调度器 ===")
    print()
    
    scheduler = MonitorScheduler()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            scheduler.list_tasks()
        
        elif command == 'add':
            if len(sys.argv) < 3:
                print("用法: python schedule-monitor.py add <任务ID>")
                return
            
            task_id = sys.argv[2]
            
            # 创建示例任务配置
            task_config = {
                "name": f"任务-{task_id}",
                "enabled": True,
                "type": "custom",
                "schedule": {
                    "type": "interval",
                    "interval": 300
                },
                "monitor_config": {
                    "script": "simple-monitor.py",
                    "config": f"{task_id}_config.json"
                },
                "description": "自定义监控任务",
                "last_run": None
            }
            
            scheduler.add_task(task_id, task_config)
            print(f"已添加任务: {task_id}")
            print("请编辑配置文件以设置具体监控条件")
        
        elif command == 'remove':
            if len(sys.argv) < 3:
                print("用法: python schedule-monitor.py remove <任务ID>")
                return
            
            task_id = sys.argv[2]
            scheduler.remove_task(task_id)
        
        elif command == 'run':
            if len(sys.argv) < 3:
                print("用法: python schedule-monitor.py run <任务ID>")
                return
            
            task_id = sys.argv[2]
            scheduler.run_task_now(task_id)
        
        elif command == 'init':
            # 初始化示例任务
            example_tasks = create_example_task()
            for task_id, config in example_tasks.items():
                scheduler.add_task(task_id, config)
            
            print("已初始化示例任务")
            scheduler.list_tasks()
        
        else:
            print(f"未知命令: {command}")
            print_help()
    
    else:
        print_help()

def print_help():
    """打印帮助信息"""
    print("可用命令:")
    print("  list              - 列出所有定时任务")
    print("  add <任务ID>      - 添加新任务")
    print("  remove <任务ID>   - 移除任务")
    print("  run <任务ID>      - 立即运行任务")
    print("  init              - 初始化示例任务")
    print()
    print("示例:")
    print("  python schedule-monitor.py list")
    print("  python schedule-monitor.py add website_check")
    print("  python schedule-monitor.py run website_check")
    print()
    print("注意: 需要先配置监控脚本和配置文件")

if __name__ == "__main__":
    main()