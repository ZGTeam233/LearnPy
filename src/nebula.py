#!/usr/bin/env python3
"""
终端星云 - 使用ASCII字符和颜色模拟宇宙星云
基于噪声函数生成不断流动的彩色星云图案
"""
import math
import time
import sys
import os


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def noise(x, y, z):
    """简单的伪随机噪声函数"""
    x = math.sin(x * 12.9898 + y * 78.233 + z * 42.345) * 43758.5453
    return x - math.floor(x)


def fractal_noise(x, y, t):
    """分形噪声，产生更自然的结构"""
    value = 0.0
    amplitude = 0.5
    frequency = 1.0

    for _ in range(4):  # 4层分形叠加
        value += amplitude * noise(x * frequency, y * frequency, t)
        amplitude *= 0.5
        frequency *= 2.0

    return value


def render_nebula(width, height, time_offset):
    """渲染一帧星云"""
    frame = []
    chars = " .:!*%$#@"  # 字符表示亮度梯度

    for y in range(height):
        line = []
        for x in range(width):
            # 归一化坐标
            nx = x / width * 2.0 - 1.0
            ny = y / height * 2.0 - 1.0

            # 生成三个通道的噪声
            r = fractal_noise(nx, ny, time_offset)
            g = fractal_noise(nx + 5.2, ny + 3.7, time_offset + 10.0)
            b = fractal_noise(nx - 2.3, ny - 4.1, time_offset + 20.0)

            # 组合亮度
            brightness = (r * 0.3 + g * 0.5 + b * 0.2)
            brightness = max(0, min(1, brightness * 2 - 0.3))

            # 选择字符
            char_idx = int(brightness * (len(chars) - 1))
            char = chars[char_idx]

            # 生成渐变色 (紫色到蓝色到青色)
            if brightness < 0.3:
                color = 95  # 深紫色
            elif brightness < 0.6:
                color = 35  # 蓝绿色
            else:
                color = 46  # 青色

            line.append(f'\033[38;5;{color}m{char}\033[0m')
        frame.append(''.join(line))

    return frame


def main():
    """主程序"""
    print("\033[?25l")  # 隐藏光标
    print("\033[2J")  # 清屏

    width = 80
    height = 30
    time_offset = 0.0

    try:
        while True:
            # 移动到屏幕左上角
            print(f"\033[H", end="")

            # 渲染和显示星云
            nebula = render_nebula(width, height, time_offset)
            for line in nebula:
                print(line)

            # 显示信息
            print(f"\n\033[90m🌀 流动星云 | 时间: {time_offset:.1f} | Ctrl+C 退出\033[0m")

            time_offset += 0.05  # 时间流逝
            time.sleep(0.1)  # 控制帧率

    except KeyboardInterrupt:
        print("\033[?25h")  # 恢复光标
        print("\n\033[92m✨ 星云归于寂静...\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    main()