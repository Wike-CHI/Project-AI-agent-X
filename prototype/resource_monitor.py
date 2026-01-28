#!/usr/bin/env python3
"""
===============================================================================
资源监控脚本 - Qwen 2.5 3B 原型验证

功能:
- 监控 CPU、内存、GPU 使用情况
- 记录 Ollama 服务状态
- 生成资源使用报告

安装依赖:
    pip install psutil GPUtil

用法:
    python resource_monitor.py                    # 交互模式
    python resource_monitor.py --duration 300     # 监控 5 分钟
    python resource_monitor.py --output report.json  # 输出到 JSON 文件
===============================================================================
"""

import argparse
import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil 未安装，内存/CPU 监控将受限")

try:
    import GPUtil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False
    print("Warning: GPUtil 未安装，GPU 监控将不可用")


class ResourceSample:
    """资源采样数据"""

    def __init__(self):
        self.timestamp: float = time.time()
        self.datetime: str = datetime.now().isoformat()
        self.memory_percent: float = 0.0
        self.memory_used_gb: float = 0.0
        self.memory_available_gb: float = 0.0
        self.cpu_percent: float = 0.0
        self.cpu_count: int = psutil.cpu_count() if HAS_PSUTIL else 0
        self.disk_usage_percent: float = 0.0
        self.ollama_memory_mb: float = 0.0
        self.gpu_memory_percent: Optional[float] = None
        self.gpu_memory_used_mb: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "datetime": self.datetime,
            "memory": {
                "percent": self.memory_percent,
                "used_gb": self.memory_used_gb,
                "available_gb": self.memory_available_gb
            },
            "cpu": {
                "percent": self.cpu_percent,
                "count": self.cpu_count
            },
            "disk": {
                "usage_percent": self.disk_usage_percent
            },
            "ollama": {
                "memory_mb": self.ollama_memory_mb
            },
            "gpu": {
                "memory_percent": self.gpu_memory_percent,
                "memory_used_mb": self.gpu_memory_used_mb
            }
        }


class ResourceMonitor:
    """资源监控器"""

    def __init__(
        self,
        ollama_process_name: str = "ollama",
        sample_interval: float = 1.0
    ):
        self.ollama_process_name = ollama_process_name
        self.sample_interval = sample_interval
        self.samples: List[ResourceSample] = []
        self.running = False
        self._lock = threading.Lock()

    def get_system_resources(self) -> ResourceSample:
        """获取系统资源使用情况"""
        sample = ResourceSample()

        if HAS_PSUTIL:
            # 内存
            mem = psutil.virtual_memory()
            sample.memory_percent = mem.percent
            sample.memory_used_gb = mem.used / (1024 ** 3)
            sample.memory_available_gb = mem.available / (1024 ** 3)

            # CPU
            sample.cpu_percent = psutil.cpu_percent(interval=0.1)

            # 磁盘
            disk = psutil.disk_usage('/')
            sample.disk_usage_percent = disk.percent

            # Ollama 进程内存
            sample.ollama_memory_mb = self._get_ollama_memory_mb()

        # GPU
        if HAS_GPUTIL:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # 使用第一个 GPU
                    sample.gpu_memory_percent = (gpu.memoryUsed / gpu.memoryTotal) * 100
                    sample.gpu_memory_used_mb = gpu.memoryUsed
            except Exception as e:
                pass

        return sample

    def _get_ollama_memory_mb(self) -> float:
        """获取 Ollama 进程内存使用"""
        total_memory = 0.0
        try:
            for proc in psutil.process_iter(['name', 'memory_info']):
                if proc.info['name'] and 'ollama' in proc.info['name'].lower():
                    mem_info = proc.info.get('memory_info')
                    if mem_info:
                        total_memory += mem_info.rss / (1024 * 1024)
        except Exception:
            pass
        return total_memory

    def start(
        self,
        duration: Optional[float] = None,
        output_file: Optional[str] = None,
        quiet: bool = False
    ):
        """
        开始监控

        Args:
            duration: 监控时长（秒），None 表示无限
            output_file: 输出文件路径
            quiet: 安静模式，不输出实时信息
        """
        self.running = True
        self.samples = []

        if not quiet:
            print("=" * 60)
            print("  资源监控器 - Qwen 2.5 3B 验证")
            print("=" * 60)
            print(f"采样间隔: {self.sample_interval}秒")
            if duration:
                print(f"监控时长: {duration}秒")
            else:
                print("监控时长: 无限 (按 Ctrl+C 停止)")
            print("-" * 60)

        start_time = time.time()

        try:
            while self.running:
                # 检查时长限制
                if duration and (time.time() - start_time) >= duration:
                    break

                # 采样
                sample = self.get_system_resources()

                with self._lock:
                    self.samples.append(sample)

                # 输出实时信息
                if not quiet:
                    self._print_sample(sample)

                # 等待
                time.sleep(self.sample_interval)

        except KeyboardInterrupt:
            print("\n监控已停止")

        # 生成报告
        if self.samples:
            report = self.generate_report()

            if output_file:
                self._save_report(report, output_file)
            else:
                self._print_report(report)

    def stop(self):
        """停止监控"""
        self.running = False

    def _print_sample(self, sample: ResourceSample):
        """打印采样信息"""
        mem_gb = sample.memory_used_gb
        mem_bar = self._make_bar(mem_gb / 8, 8)  # 假设 8GB 总内存

        print(
            f"\r内存: {mem_gb:.2f}GB {mem_bar} | "
            f"CPU: {sample.cpu_percent:5.1f}% | "
            f"Ollama: {sample.ollama_memory_mb:6.1f}MB",
            end="", flush=True
        )

    def _make_bar(self, value: float, max_value: float) -> str:
        """生成进度条"""
        bar_length = 20
        filled = int(bar_length * value / max_value)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"[{bar}]"

    def generate_report(self) -> dict:
        """生成监控报告"""
        if not self.samples:
            return {}

        samples = self.samples

        # 计算统计
        memory_samples = [s.memory_percent for s in samples]
        cpu_samples = [s.cpu_percent for s in samples]
        ollama_samples = [s.ollama_memory_mb for s in samples]

        report = {
            "summary": {
                "start_time": samples[0].datetime,
                "end_time": samples[-1].datetime,
                "duration_seconds": samples[-1].timestamp - samples[0].timestamp,
                "sample_count": len(samples)
            },
            "memory": {
                "avg_percent": self._avg(memory_samples),
                "max_percent": max(memory_samples),
                "min_percent": min(memory_samples),
                "avg_used_gb": self._avg([s.memory_used_gb for s in samples]),
                "max_used_gb": max([s.memory_used_gb for s in samples])
            },
            "cpu": {
                "avg_percent": self._avg(cpu_samples),
                "max_percent": max(cpu_samples),
                "min_percent": min(cpu_samples)
            },
            "ollama": {
                "avg_memory_mb": self._avg(ollama_samples),
                "max_memory_mb": max(ollama_samples),
                "min_memory_mb": min(ollama_samples)
            },
            "disk": {
                "avg_usage_percent": self._avg([s.disk_usage_percent for s in samples])
            }
        }

        # GPU 统计
        gpu_samples = [s for s in samples if s.gpu_memory_percent is not None]
        if gpu_samples:
            report["gpu"] = {
                "avg_memory_percent": self._avg([s.gpu_memory_percent for s in gpu_samples]),
                "max_memory_percent": max([s.gpu_memory_percent for s in gpu_samples]),
                "avg_memory_mb": self._avg([s.gpu_memory_used_mb for s in gpu_samples])
            }

        # 评估结果
        report["evaluation"] = self._evaluate_report(report)

        return report

    def _avg(self, values: List[float]) -> float:
        """计算平均值"""
        return sum(values) / len(values) if values else 0.0

    def _evaluate_report(self, report: dict) -> dict:
        """评估监控结果"""
        evaluation = {
            "memory": {
                "status": "UNKNOWN",
                "message": ""
            },
            "cpu": {
                "status": "UNKNOWN",
                "message": ""
            },
            "ollama": {
                "status": "UNKNOWN",
                "message": ""
            },
            "overall": {
                "status": "UNKNOWN",
                "passed": False
            }
        }

        # 内存评估 (目标: < 4GB 含系统)
        max_memory_gb = report.get("memory", {}).get("max_used_gb", 0)
        if max_memory_gb < 4.0:
            evaluation["memory"]["status"] = "PASS"
            evaluation["memory"]["message"] = f"最大内存 {max_memory_gb:.2f}GB < 4GB 目标"
            evaluation["memory"]["passed"] = True
        elif max_memory_gb < 6.0:
            evaluation["memory"]["status"] = "WARNING"
            evaluation["memory"]["message"] = f"内存 {max_memory_gb:.2f}GB 较高，但可接受"
            evaluation["memory"]["passed"] = True
        else:
            evaluation["memory"]["status"] = "FAIL"
            evaluation["memory"]["message"] = f"内存 {max_memory_gb:.2f}GB 超过 6GB 限制"
            evaluation["memory"]["passed"] = False

        # CPU 评估 (目标: < 80%)
        max_cpu = report.get("cpu", {}).get("max_percent", 0)
        if max_cpu < 80:
            evaluation["cpu"]["status"] = "PASS"
            evaluation["cpu"]["passed"] = True
        else:
            evaluation["cpu"]["status"] = "WARNING"
            evaluation["cpu"]["passed"] = True

        # Ollama 评估 (目标: < 3GB)
        max_ollama_mb = report.get("ollama", {}).get("max_memory_mb", 0)
        if max_ollama_mb < 3072:
            evaluation["ollama"]["status"] = "PASS"
            evaluation["ollama"]["message"] = f"Ollama {max_ollama_mb:.0f}MB < 3GB"
            evaluation["ollama"]["passed"] = True
        else:
            evaluation["ollama"]["status"] = "WARNING"
            evaluation["ollama"]["message"] = f"Ollama {max_ollama_mb:.0f}MB 较高"
            evaluation["ollama"]["passed"] = True

        # 综合评估
        all_passed = all(e.get("passed", False) for e in [
            evaluation["memory"],
            evaluation["cpu"],
            evaluation["ollama"]
        ])

        if all_passed:
            evaluation["overall"]["status"] = "PASS"
            evaluation["overall"]["message"] = "所有指标达到预期"
            evaluation["overall"]["passed"] = True
        else:
            evaluation["overall"]["status"] = "WARNING"
            evaluation["overall"]["message"] = "部分指标未达最佳"
            evaluation["overall"]["passed"] = True

        return evaluation

    def _print_report(self, report: dict):
        """打印报告"""
        print("\n" + "=" * 60)
        print("  资源监控报告")
        print("=" * 60)

        summary = report.get("summary", {})
        print(f"监控时长: {summary.get('duration_seconds', 0):.1f}秒")
        print(f"采样次数: {summary.get('sample_count', 0)}")
        print("-" * 60)

        mem = report.get("memory", {})
        print(f"内存使用:")
        print(f"  平均: {mem.get('avg_percent', 0):.1f}% ({mem.get('avg_used_gb', 0):.2f}GB)")
        print(f"  最大: {mem.get('max_percent', 0):.1f}% ({mem.get('max_used_gb', 0):.2f}GB)")

        cpu = report.get("cpu", {})
        print(f"CPU 使用:")
        print(f"  平均: {cpu.get('avg_percent', 0):.1f}%")
        print(f"  最大: {cpu.get('max_percent', 0):.1f}%")

        ollama = report.get("ollama", {})
        print(f"Ollama 内存:")
        print(f"  平均: {ollama.get('avg_memory_mb', 0):.0f}MB")
        print(f"  最大: {ollama.get('max_memory_mb', 0):.0f}MB")

        print("-" * 60)
        print("评估结果:")

        evaluation = report.get("evaluation", {})
        for component, result in evaluation.items():
            if component == "overall":
                continue
            status_icon = "✓" if result.get("passed") else "!"
            print(f"  [{status_icon}] {component}: {result.get('status')} - {result.get('message', '')}")

        print(f"\n综合: {evaluation.get('overall', {}).get('status')}")
        print(f"消息: {evaluation.get('overall', {}).get('message', '')}")

    def _save_report(self, report: dict, output_file: str):
        """保存报告到文件"""
        # 保存完整 JSON
        json_file = output_file if output_file.endswith('.json') else f"{output_file}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n完整报告已保存: {json_file}")

        # 保存 CSV
        csv_file = output_file if output_file.endswith('.csv') else f"{output_file}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.samples:
                headers = list(self.samples[0].to_dict().keys())
                f.write(','.join(headers) + '\n')
                for sample in self.samples:
                    d = sample.to_dict()
                    # 扁平化
                    row = [
                        str(d.get('timestamp', '')),
                        d.get('datetime', ''),
                        str(d.get('memory', {}).get('percent', '')),
                        str(d.get('memory', {}).get('used_gb', '')),
                        str(d.get('cpu', {}).get('percent', '')),
                        str(d.get('ollama', {}).get('memory_mb', ''))
                    ]
                    f.write(','.join(row) + '\n')
        print(f"CSV 数据已保存: {csv_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Qwen 2.5 3B 资源监控器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python resource_monitor.py                          # 交互监控
  python resource_monitor.py --duration 300           # 监控 5 分钟
  python resource_monitor.py --output report          # 保存报告
  python resource_monitor.py --quiet --duration 60    # 安静模式
        """
    )

    parser.add_argument(
        '-d', '--duration',
        type=float,
        default=None,
        help='监控时长（秒）'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='输出文件路径（不含扩展名）'
    )

    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=1.0,
        help='采样间隔（秒），默认 1.0'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='安静模式，不输出实时信息'
    )

    args = parser.parse_args()

    # 检查依赖
    if not HAS_PSUTIL:
        print("错误: 需要安装 psutil")
        print("运行: pip install psutil")
        sys.exit(1)

    # 创建监控器
    monitor = ResourceMonitor(sample_interval=args.interval)

    # 开始监控
    try:
        monitor.start(
            duration=args.duration,
            output_file=args.output,
            quiet=args.quiet
        )
    except KeyboardInterrupt:
        print("\n正在停止监控...")
        monitor.stop()


if __name__ == "__main__":
    main()
