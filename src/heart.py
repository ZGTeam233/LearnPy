"""
跳动的心脏 - 字符动画
在终端中显示一个彩色跳动的爱心图案
"""
import time
import sys
import os


def clear_screen():
    """清屏函数，适配不同操作系统"""
    os.system('cls' if os.name == 'nt' else 'clear')


def heart_frame(scale, frame_num):
    """生成爱心图案的一帧"""
    # 爱心函数：(x²+y²-1)³ - x²y³ = 0
    frames = []

    # 两帧循环实现跳动效果
    if frame_num % 2 == 0:
        scale *= 1.1  # 放大一点

    for y in range(int(-15 * scale), int(15 * scale)):
        line = []
        for x in range(int(-30 * scale), int(30 * scale)):
            # 坐标变换
            x_scaled = x / (20 * scale)
            y_scaled = y / (12 * scale)

            # 爱心方程
            f = (x_scaled ** 2 + y_scaled ** 2 - 1) ** 3 - x_scaled ** 2 * y_scaled ** 3

            if f <= 0:
                # 根据位置选择颜色和字符
                dist = (x_scaled ** 2 + y_scaled ** 2) ** 0.5
                if dist < 0.3:
                    line.append('\033[91m█\033[0m')  # 亮红色
                elif dist < 0.6:
                    line.append('\033[31m▓\033[0m')  # 红色
                elif dist < 0.8:
                    line.append('\033[31m▒\033[0m')  # 浅红色
                else:
                    line.append('\033[31m░\033[0m')  # 淡红色
            else:
                line.append(' ')
        frames.append(''.join(line))

    return frames


def main():
    """主函数"""
    print("\033[?25l")  # 隐藏光标

    try:
        frame = 0
        while True:
            clear_screen()

            # 显示标题
            print("\n" + " " * 15 + "\033[1;95m❤️ 跳动的心脏 ❤️\033[0m\n")

            # 生成并显示爱心
            heart = heart_frame(1.0, frame)
            for line in heart:
                print(line)

            # 显示底部信息
            print(f"\n\033[90m帧数: {frame}  |  按 Ctrl+C 退出\033[0m")

            frame += 1
            time.sleep(0.3)  # 控制帧率

    except KeyboardInterrupt:
        print("\033[?25h")  # 恢复光标
        print("\n\033[92m程序已退出。感谢观看！\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    main()