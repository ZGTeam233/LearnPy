import sys
import random
import time
import os
from math import sin, cos, radians

# ANSI颜色代码
COLORS = [
    '\033[38;5;196m',  # 红
    '\033[38;5;11m',  # 黄
    '\033[38;5;33m',  # 蓝
    '\033[38;5;46m',  # 绿
    '\033[38;5;201m',  # 粉
    '\033[38;5;214m',  # 紫
    '\033[38;5;226m'  # 白
]


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


class Firework:
    def __init__(self):
        self.x = random.randint(10, 110)
        self.y = 30
        self.angle = radians(random.randint(0, 360))
        self.speed = random.uniform(2, 4)
        self.life = 0
        self.particles = []
        self.color = random.choice(COLORS)
        self.exploded = False

    def update(self):
        if not self.exploded:
            self.y -= self.speed
            self.speed *= 0.95
            if self.y < 1:
                self.explode()
        else:
            self.life += 1
            self.particles = [
                (
                    p[0] + cos(p[2]) * p[3],
                    p[1] + sin(p[2]) * p[3],
                    p[2],
                    p[3] * 0.9
                )
                for p in self.particles
            ]
            self.particles = [p for p in self.particles if p[3] > 0.1]

    def explode(self):
        self.exploded = True
        self.particles = [
            (self.x, self.y, radians(random.randint(0, 360)), random.uniform(1, 2))
            for _ in range(100)
        ]


def main():
    clear()
    print('\033[?25l')  # 隐藏光标
    fireworks = []

    try:
        while True:
            # 生成新烟花
            if random.random() < 0.1:
                fireworks.append(Firework())

            # 更新所有烟花
            for fw in fireworks:
                fw.update()

            # 渲染
            sys.stdout.write('\033[H\033[J')  # 清屏
            for fw in fireworks:
                if fw.exploded:
                    for (x, y, _, _) in fw.particles:
                        sys.stdout.write(f'\033[{int(y)};{int(x)}H{fw.color}*\033[0m')

            # 播放音效（需要支持ANSI声音）
            sys.stdout.write('\a')

            time.sleep(0.05)

    except KeyboardInterrupt:
        print('\033[?25h')  # 恢复光标
        clear()


if __name__ == '__main__':
    main()