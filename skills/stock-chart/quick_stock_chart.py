#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速股票图表 - 简化版本
确保能立即看到结果
"""

import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import sys

print("=" * 60)
print("快速股票图表工具")
print("=" * 60)

if len(sys.argv) < 2:
    print("使用: python quick_stock_chart.py <股票>")
    print("示例: python quick_stock_chart.py 600519")
    print("示例: python quick_stock_chart.py 贵州茅台")
    sys.exit(1)

stock_input = sys.argv[1]

# 股票映射
stock_map = {
    '贵州茅台': 'sh600519',
    '茅台': 'sh600519',
    '五粮液': 'sz000858',
    '宁德时代': 'sz300750',
    '上证指数': 'sh000001',
}

# 获取股票代码
if stock_input in stock_map:
    code = stock_map[stock_input]
elif stock_input.startswith(('sh', 'sz')):
    code = stock_input
elif stock_input.isdigit() and len(stock_input) == 6:
    if stock_input.startswith(('60', '68')):
        code = f"sh{stock_input}"
    else:
        code = f"sz{stock_input}"
else:
    print(f"错误: 无法识别 {stock_input}")
    sys.exit(1)

print(f"查询股票: {code}")

# 获取数据
url = f"https://hq.sinajs.cn/list={code}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn/'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'gbk'
    
    if response.status_code == 200:
        content = response.text
        if f'hq_str_{code}="' in content:
            data_str = content.split('="')[1].split('"')[0]
            data_parts = data_str.split(',')
            
            if len(data_parts) >= 30:
                name = data_parts[0]
                price = float(data_parts[3])
                open_price = float(data_parts[1])
                high = float(data_parts[4])
                low = float(data_parts[5])
                prev_close = float(data_parts[2])
                
                # 计算涨跌
                change = price - prev_close
                if prev_close != 0:
                    change_percent = (change / prev_close) * 100
                else:
                    change_percent = 0
                
                print(f"股票名称: {name}")
                print(f"当前价格: {price:.2f}元")
                print(f"今日涨跌: {change:+.2f} ({change_percent:+.2f}%)")
                print(f"开盘: {open_price:.2f}, 最高: {high:.2f}, 最低: {low:.2f}")
                
                # 生成简单图表
                # 时间点
                times = ['09:30', '10:00', '10:30', '11:00', '11:30', '13:00', '13:30', '14:00', '14:30', '15:00']
                
                # 价格点（模拟）
                prices = []
                for i in range(len(times)):
                    progress = i / (len(times) - 1)
                    if price >= open_price:
                        # 上涨
                        trend = np.sin(progress * np.pi) * (high - open_price) * 0.3
                    else:
                        # 下跌
                        trend = -np.sin(progress * np.pi) * (open_price - low) * 0.3
                    
                    p = open_price + trend
                    prices.append(p)
                
                # 最后一个点是当前价格
                prices[-1] = price
                
                # 创建图表
                plt.figure(figsize=(10, 6))
                
                # 线条颜色
                line_color = 'red' if price >= open_price else 'green'
                
                plt.plot(times, prices, color=line_color, linewidth=2, marker='o')
                
                # 标题
                change_symbol = "↑" if change >= 0 else "↓"
                plt.title(f"{name}\n当前: {price:.2f}元 {change_symbol} {change:+.2f} ({change_percent:+.2f}%)", fontsize=14)
                
                plt.xlabel('时间')
                plt.ylabel('价格 (元)')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                
                # 关键价格线
                plt.axhline(y=open_price, color='orange', linestyle='--', alpha=0.7, label=f'开盘 {open_price:.2f}')
                plt.axhline(y=prev_close, color='blue', linestyle='--', alpha=0.7, label=f'昨收 {prev_close:.2f}')
                
                plt.legend()
                plt.tight_layout()
                
                # 保存图表
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{code}_{timestamp}.png"
                plt.savefig(filename, dpi=100)
                
                print(f"\n图表已生成: {filename}")
                print("正在显示图表窗口...")
                
                # 显示图表
                plt.show()
                
                print("\n操作完成!")
                
            else:
                print("数据格式错误")
    else:
        print(f"HTTP错误: {response.status_code}")
        
except Exception as e:
    print(f"错误: {e}")