"""CPU/GPU detection for transcription.

GPU means an NVIDIA card with CUDA. faster-whisper (CTranslate2) needs the NVIDIA
driver plus cuBLAS; cuDNN ships inside the ctranslate2 wheel. cuBLAS comes from the
optional `gpu` extra (`uv sync --extra gpu`), which installs it under
site-packages/nvidia/*/bin, so those folders are added to the DLL search path here.
"""

from __future__ import annotations

import functools
import os
import subprocess
import sys
from pathlib import Path

CUDA_LIBS = ("cublas64_12.dll", "cublasLt64_12.dll") if os.name == "nt" else ("libcublas.so.12",)


def add_cuda_dll_dirs() -> None:
    """Make pip-installed NVIDIA libraries loadable (Windows doesn't search site-packages)."""
    if os.name != "nt":
        return
    for base in map(Path, sys.path):
        nvidia = base / "nvidia"
        if not nvidia.is_dir():
            continue
        for bin_dir in nvidia.glob("*/bin"):
            os.add_dll_directory(str(bin_dir))
            os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"


@functools.lru_cache(maxsize=1)
def gpu_info() -> dict:
    """What the GPU option can do on this machine. Cached: hardware doesn't change while
    the app runs."""
    add_cuda_dll_dirs()
    try:
        import ctranslate2

        count = ctranslate2.get_cuda_device_count()
    except Exception:
        count = 0
    name = _nvidia_name() if count else None
    libs = _cuda_libs_loadable() if count else False
    if not count:
        reason = "No NVIDIA GPU detected."
    elif not libs:
        reason = "NVIDIA GPU found, but the GPU libraries aren't installed. Run: uv sync --extra gpu"
    else:
        reason = None
    return {"available": bool(count and libs), "detected": bool(count), "name": name, "reason": reason}


@functools.lru_cache(maxsize=1)
def cpu_name() -> str:
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                return str(winreg.QueryValueEx(key, "ProcessorNameString")[0]).strip()
        except OSError:
            pass
    import platform

    return platform.processor() or "CPU"


def resolve(setting: str) -> str:
    """The device to try for a job: 'cuda' only when the user chose GPU and it's usable."""
    return "cuda" if setting == "gpu" and gpu_info()["available"] else "cpu"


def _nvidia_name() -> str | None:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return out.stdout.strip().splitlines()[0] if out.returncode == 0 and out.stdout.strip() else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _cuda_libs_loadable() -> bool:
    import ctypes

    loader = ctypes.WinDLL if os.name == "nt" else ctypes.CDLL
    try:
        for lib in CUDA_LIBS:
            loader(lib)
        return True
    except OSError:
        return False
