#!/usr/bin/env python3

#
# Created by wsnzg6 on 2026/10/8.
# Copyright(c) 2026 ZGTeam233.
#

"""
vocal_sep.py
基于 Demucs 的 OOP 人声分离脚本。

用法示例：
    python separate.py input.mp3
    python separate.py input.mp3 -o out
    python separate.py input.mp3 -m htdemucs_ft --two-stems vocals
    python separate.py input.mp3 --two-stems ""       # 分离全部 4 轨
"""

from __future__ import annotations

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import argparse
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# 关掉 Windows 上常见的那条 HuggingFace symlink 警告
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch
from demucs.api import Separator as DemucsSeparator, save_audio


# ---------------------------------------------------------------------------
# 结果对象
# ---------------------------------------------------------------------------
@dataclass
class SeparationResult:
    """保存一次分离任务的结果信息。"""

    source: Path
    output_dir: Path
    stems: Dict[str, Path] = field(default_factory=dict)
    elapsed: float = 0.0

    @property
    def vocals(self) -> Optional[Path]:
        """人声轨道。"""
        return self.stems.get("vocals")

    @property
    def accompaniment(self) -> Optional[Path]:
        """伴奏。two_stems 模式里叫 no_vocals，全轨模式里一般指 other。"""
        return self.stems.get("no_vocals") or self.stems.get("other")

    def __str__(self) -> str:
        lines = [
            f"源文件 : {self.source}",
            f"输出目录: {self.output_dir}",
            f"耗时   : {self.elapsed:.1f}s",
        ]
        for name, path in self.stems.items():
            lines.append(f"  - {name:10s} -> {path.name}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主类
# ---------------------------------------------------------------------------
class StemSeparator:
    """Demucs 的面向对象封装。"""

    AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".opus", ".wma"}
    DEFAULT_MODEL = "htdemucs"

    # 常见模型，供参考：
    #   htdemucs      - 默认，质量/速度均衡
    #   htdemucs_ft   - 精调版，慢一些但更干净
    #   htdemucs_6s   - 6 轨（含 piano / guitar），仅 htdemucs_6s 支持
    #   mdx_extra     - MDX 系高质量模型
    KNOWN_MODELS = ("htdemucs", "htdemucs_ft", "htdemucs_6s", "mdx_extra", "mdx_extra_q")

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        device: Optional[str] = None,
        output_root: str | Path = "separated",
        shifts: int = 1,
        overlap: float = 0.25,
        progress: bool = True,
    ) -> None:
        self.model = model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.output_root = Path(output_root)
        self.shifts = shifts
        self.overlap = overlap
        self.progress = progress

        self._impl: Optional[DemucsSeparator] = None  # 懒加载

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------
    def separate(
        self,
        audio_path: str | Path,
        output_dir: Optional[str | Path] = None,
        two_stems: Optional[str] = "vocals",
    ) -> SeparationResult:
        """
        分离单个音频文件。

        Args:
            audio_path: 输入音频路径。
            output_dir: 输出目录；None 时用 output_root/<model>/<文件名>/。
            two_stems: 只保留该 stem 及其"伴奏"（no_xxx）；None 表示输出全部轨道。

        Returns:
            SeparationResult
        """
        src = self._validate_input(audio_path)
        impl = self._load_model()
        out_dir = self._prepare_output_dir(src, output_dir)

        print(f"[i] 开始分离 {src.name}")
        print(f"    模型 = {self.model} | 设备 = {self.device}")
        t0 = time.time()

        _, separated = impl.separate_audio_file(str(src))

        if two_stems:
            separated = self._merge_to_two_stems(separated, two_stems)

        result = SeparationResult(source=src, output_dir=out_dir)
        for name, tensor in separated.items():
            path = out_dir / f"{name}.wav"
            save_audio(tensor, str(path), samplerate=impl.samplerate)
            result.stems[name] = path
            print(f"    -> {path.name}")

        result.elapsed = time.time() - t0
        print(f"[✓] 完成，用时 {result.elapsed:.1f}s")
        return result

    def separate_many(
        self,
        paths: Iterable[str | Path],
        two_stems: Optional[str] = "vocals",
    ) -> List[SeparationResult]:
        """批量处理，跳过失败的文件。"""
        results: List[SeparationResult] = []
        for p in paths:
            try:
                results.append(self.separate(p, two_stems=two_stems))
            except Exception as exc:  # noqa: BLE001
                print(f"[X] {p} 处理失败: {exc}", file=sys.stderr)
        return results

    # ------------------------------------------------------------------
    # 内部实现
    # ------------------------------------------------------------------
    def _validate_input(self, audio_path: str | Path) -> Path:
        p = Path(audio_path).expanduser()
        if not p.is_file():
            raise FileNotFoundError(f"找不到文件: {p}")
        if p.suffix.lower() not in self.AUDIO_EXTS:
            print(f"[!] 警告: {p.suffix} 不在常见音频格式里，仍会尝试处理", file=sys.stderr)
        return p

    def _load_model(self) -> DemucsSeparator:
        """第一次调用时加载模型权重（会触发下载 / 读取缓存）。"""
        if self._impl is None:
            print(f"[i] 加载模型 {self.model} ...")
            self._impl = DemucsSeparator(
                model=self.model,
                device=self.device,
                shifts=self.shifts,
                overlap=self.overlap,
                progress=self.progress,
            )
        return self._impl

    def _prepare_output_dir(self, src: Path, output_dir: Optional[str | Path]) -> Path:
        out = Path(output_dir) if output_dir else self.output_root / self.model / src.stem
        out.mkdir(parents=True, exist_ok=True)
        return out

    @staticmethod
    def _merge_to_two_stems(
        separated: Dict[str, torch.Tensor],
        keep: str,
    ) -> Dict[str, torch.Tensor]:
        """把多轨结果合并成 {keep, no_keep} 两轨。"""
        if keep not in separated:
            raise ValueError(
                f"模型输出里没有 '{keep}' 轨道，可选: {list(separated.keys())}"
            )
        others = [v for k, v in separated.items() if k != keep]
        if not others:
            return {keep: separated[keep]}
        merged = torch.stack(others, dim=0).sum(dim=0)
        return {keep: separated[keep], f"no_{keep}": merged}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="基于 Demucs 的音乐人声分离（OOP 版）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("audio", help="输入音频文件路径")
    p.add_argument("-o", "--output", default=None,
                   help="输出目录（默认 separated/<model>/<文件名>/）")
    p.add_argument("-m", "--model", default=StemSeparator.DEFAULT_MODEL,
                   choices=StemSeparator.KNOWN_MODELS,
                   help="Demucs 模型名")
    p.add_argument("-d", "--device", default=None, help="cpu / cuda / mps（默认自动）")
    p.add_argument("--two-stems", default="vocals",
                   help="只输出该 stem 及其伴奏（no_xxx）；设为 '' 输出全部轨道")
    p.add_argument("--shifts", type=int, default=1, help="移位次数，越大越慢越稳")
    p.add_argument("--overlap", type=float, default=0.25, help="分块重叠比例")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    separator = StemSeparator(
        model=args.model,
        device=args.device,
        shifts=args.shifts,
        overlap=args.overlap,
    )

    try:
        result = separator.separate(
            args.audio,
            output_dir=args.output,
            two_stems=args.two_stems or None,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[X] 失败: {exc}", file=sys.stderr)
        return 1

    print()
    print(result)
    if result.accompaniment:
        print(f"\n伴奏已生成: {result.accompaniment}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())