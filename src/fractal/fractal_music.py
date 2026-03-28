#!/usr/bin/env python3
"""
分形音乐生成器 - 实时音频合成
通过曼德博集合的逃逸时间算法生成旋律
"""
import numpy as np
import sounddevice as sd
import threading
import time
import sys


class FractalSynth:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.time = 0
        self.freq_base = 220  # A3 基频
        self.playing = True

        # 分形参数
        self.c_real = 0.0
        self.c_imag = 0.0
        self.x_pos = -2.0
        self.y_pos = -1.5

    def mandelbrot(self, x, y, max_iter=100):
        """计算曼德博集合的迭代次数"""
        z_real, z_imag = 0, 0
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag

            if z_real_sq + z_imag_sq > 4.0:
                return i  # 逃逸

            # z = z² + c
            z_imag = 2 * z_real * z_imag + y
            z_real = z_real_sq - z_imag_sq + x

        return max_iter  # 未逃逸

    def generate_frame(self, frame_count):
        """生成音频帧"""
        t = np.arange(self.time, self.time + frame_count / self.sample_rate,
                      1 / self.sample_rate)
        self.time += frame_count / self.sample_rate

        # 扫描曼德博集合
        scan_x = self.x_pos + 0.01 * np.sin(0.3 * self.time)
        scan_y = self.y_pos + 0.01 * np.cos(0.2 * self.time)

        # 生成音频信号
        signal = np.zeros(frame_count)

        for i in range(frame_count):
            # 当前分形坐标
            x = scan_x + (i / frame_count) * 3.0 / 10
            y = scan_y

            # 计算逃逸时间
            escape = self.mandelbrot(x, y, 50)

            if escape < 50:  # 如果在集合边界
                # 逃逸时间映射到频率
                freq = self.freq_base * (1 + (escape % 12) / 12)

                # 生成谐波
                signal[i] = 0.0
                for harmonic in range(1, 6):
                    amplitude = 0.7 / harmonic
                    phase = 2 * np.pi * freq * harmonic * t[i]
                    signal[i] += amplitude * np.sin(phase)

                # 包络
                envelope = np.exp(-0.001 * (i % 100))
                signal[i] *= envelope

        return signal * 0.3  # 降低音量

    def audio_callback(self, outdata, frames, time_info, status):
        """音频回调函数"""
        if status:
            print(f"音频状态: {status}", file=sys.stderr)

        # 生成分形音频
        audio = self.generate_frame(frames)
        outdata[:] = audio.reshape(-1, 1)

    def run(self):
        """运行合成器"""
        print("🎵 分形音乐合成器启动中...")
        print("基于曼德博集合逃逸时间生成实时音频")
        print("按 Ctrl+C 停止播放\n")

        try:
            with sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    callback=self.audio_callback,
                    blocksize=1024
            ):
                print("🔊 音频流已打开 - 正在生成分形音乐...")

                # 显示实时参数
                while self.playing:
                    print(f"\r🎶 频率扫描: x={self.x_pos:.3f}, y={self.y_pos:.3f} "
                          f"| 时间: {self.time:.1f}s", end="")
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n🎹 音乐停止")
        except Exception as e:
            print(f"\n错误: {e}")


if __name__ == "__main__":
    # 检查依赖
    try:
        import sounddevice as sd
        import numpy as np
    except ImportError:
        print("请先安装依赖: pip install sounddevice numpy")
        sys.exit(1)

    # 创建并运行合成器
    synth = FractalSynth()
    synth.run()