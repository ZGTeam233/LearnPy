import sys
import random
import time
import os
from math import sin, cos, radians

# 更紧凑的颜色+字符
COLORS = [
    '\033[31m■\033[0m',  # 红方块
    '\033[33m□\033[0m',  # 黄方块
    '\033[34m▣\033[0m',  # 蓝方块
    '\033[32m▢\033[0m'  # 绿方块
]


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


class Firework:
    def __init__(self):
        self.x = random.randint(15, 50)  # 缩小水平范围
        self.y = 20  # 缩小垂直范围
        self.angle = radians(random.randint(0, 360))
        self.speed = random.uniform(1.5, 3)
        self.particles = []
        self.color = random.choice(COLORS)
        self.exploded = False

    def update(self):
        if not self.exploded:
            self.y -= self.speed
            self.speed *= 0.9
            if self.y < 5:  # 更早爆炸
                self.explode()
        else:
            self.particles = [
                (p[0] + cos(p[2]) * p[3], p[1] + sin(p[2]) * p[3], p[2], p[3] * 0.9)
                for p in self.particles if p[3] > 0.2
            ]

    def explode(self):
        self.exploded = True
        # 减少粒子数量，增大粒子尺寸
        self.particles = [
            (self.x, self.y, radians(random.randint(0, 360)), random.uniform(1, 1.5))
            for _ in range(30)
        ]


def main():
    clear()
    print('\033[?25l')
    fireworks = []

    try:
        while True:
            if random.random() < 0.2:  # 更频繁生成烟花
                fireworks.append(Firework())

            for fw in fireworks:
                fw.update()

            sys.stdout.write('\033[H\033[J')
            # 渲染标题
            print(" " * 10 + "\033[1;35m终端烟花秀\033[0m\n")

            for fw in fireworks:
                if fw.exploded:
                    for (x, y, _, _) in fw.particles:
                        # 限制坐标在可视区域内
                        if 0 < x < 60 and 0 < y < 25:
                            sys.stdout.write(f'\033[{int(y)};{int(x)}H{fw.color}')

            time.sleep(0.1)

    except KeyboardInterrupt:
        print('\033[?25h')
        clear()


if __name__ == '__main__':
    main()
