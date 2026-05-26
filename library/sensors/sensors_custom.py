# SPDX-License-Identifier: GPL-3.0-or-later
#
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/
#
# Copyright (C) 2021 Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This file allows to add custom data source as sensors and display them in System Monitor themes
# There is no limitation on how much custom data source classes can be added to this file
# See CustomDataExample theme for the theme implementation part

import glob
import math
import os
import platform
import threading
import time
from abc import ABC, abstractmethod
from typing import List

import psutil


class CustomDataSource(ABC):
    @abstractmethod
    def as_numeric(self) -> float:
        pass

    @abstractmethod
    def as_string(self) -> str:
        pass

    @abstractmethod
    def last_values(self) -> List[float]:
        pass


# Example for a custom data class that has numeric and text values
class ExampleCustomNumericData(CustomDataSource):
    last_val = [math.nan] * 10

    def as_numeric(self) -> float:
        self.value = 75.845
        self.last_val.append(self.value)
        self.last_val.pop(0)
        return self.value

    def as_string(self) -> str:
        return f'{self.value:>5.1f}%'

    def last_values(self) -> List[float]:
        return self.last_val


class ExampleCustomTextOnlyData(CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return "Python: " + platform.python_version()

    def last_values(self) -> List[float]:
        pass


# ---------------------------------------------------------------------------
# Per-core CPU load  (CpuCore00..CpuCore31)
# Background thread polls every 0.25 s so readings are always fresh.
# ---------------------------------------------------------------------------
_PERCPU_LOCK = threading.Lock()
_PERCPU_DATA: List[float] = []


def _percpu_worker() -> None:
    psutil.cpu_percent(percpu=True)  # prime counters; first call always returns 0
    while True:
        vals = psutil.cpu_percent(interval=0.25, percpu=True)
        with _PERCPU_LOCK:
            global _PERCPU_DATA
            _PERCPU_DATA = vals


threading.Thread(target=_percpu_worker, daemon=True, name="percpu-poller").start()


def _percpu_values() -> List[float]:
    with _PERCPU_LOCK:
        return list(_PERCPU_DATA) if _PERCPU_DATA else [0.0] * 32


class _CpuCoreBase(CustomDataSource):
    core_index: int = 0

    def as_numeric(self) -> float:
        vals = _percpu_values()
        return float(vals[self.core_index]) if self.core_index < len(vals) else 0.0

    def as_string(self) -> str:
        return f"{self.as_numeric():.0f}"

    def last_values(self) -> List[float]:
        return []


for _i in range(32):
    _cls = type(f"CpuCore{_i:02d}", (_CpuCoreBase,), {"core_index": _i})
    globals()[_cls.__name__] = _cls
del _i, _cls


# ---------------------------------------------------------------------------
# Memory in GB  (MemUsedGB, MemTotalGB)
# Framework stats.py hardcodes MB — these custom sensors provide GB at 1 d.p.
# ---------------------------------------------------------------------------
class MemUsedGB(CustomDataSource):
    def as_numeric(self) -> float:
        return psutil.virtual_memory().used / 1_073_741_824  # bytes → GiB

    def as_string(self) -> str:
        return f"{self.as_numeric():.1f} GB"

    def last_values(self) -> List[float]:
        return []


class MemTotalGB(CustomDataSource):
    def as_numeric(self) -> float:
        return psutil.virtual_memory().total / 1_073_741_824

    def as_string(self) -> str:
        return f"{self.as_numeric():.1f} GB"

    def last_values(self) -> List[float]:
        return []


# ---------------------------------------------------------------------------
# Disk I/O speeds  (DiskReadMBs, DiskWriteMBs)
# Polled via psutil.disk_io_counters() with a shared TTL cache.
# History lists for LINE_GRAPH support are managed at module level.
# as_string() calls _raw() (no history side-effect) to avoid double-append
# when the framework calls both as_numeric() and as_string() per cycle.
# ---------------------------------------------------------------------------
_HIST_SZ = 120
_DISK_IO_CACHE = {"ts": 0.0, "r_bytes": 0, "w_bytes": 0, "r_mbs": 0.0, "w_mbs": 0.0}
_DISK_READ_HIST: List[float] = []
_DISK_WRITE_HIST: List[float] = []
_DISK_READ_TS: float = 0.0
_DISK_WRITE_TS: float = 0.0


def _poll_disk_io():
    now = time.monotonic()
    if now - _DISK_IO_CACHE["ts"] < 0.8:
        return
    io = psutil.disk_io_counters()
    if _DISK_IO_CACHE["ts"] > 0:
        dt = now - _DISK_IO_CACHE["ts"]
        _DISK_IO_CACHE["r_mbs"] = (io.read_bytes - _DISK_IO_CACHE["r_bytes"]) / dt / 1_048_576
        _DISK_IO_CACHE["w_mbs"] = (io.write_bytes - _DISK_IO_CACHE["w_bytes"]) / dt / 1_048_576
    _DISK_IO_CACHE["r_bytes"] = io.read_bytes
    _DISK_IO_CACHE["w_bytes"] = io.write_bytes
    _DISK_IO_CACHE["ts"] = now


class DiskReadMBs(CustomDataSource):
    def as_numeric(self) -> float:
        global _DISK_READ_TS
        _poll_disk_io()
        val = _DISK_IO_CACHE["r_mbs"]
        now = time.monotonic()
        if now - _DISK_READ_TS > 0.1:
            _DISK_READ_TS = now
            if len(_DISK_READ_HIST) != _HIST_SZ:
                _DISK_READ_HIST[:] = [math.nan] * _HIST_SZ
            _DISK_READ_HIST.append(val)
            _DISK_READ_HIST.pop(0)
        return val

    def _raw(self) -> float:
        _poll_disk_io()
        return _DISK_IO_CACHE["r_mbs"]

    def as_string(self) -> str:
        return f"{self._raw():.1f}"

    def last_values(self) -> List[float]:
        return list(_DISK_READ_HIST)


class DiskWriteMBs(CustomDataSource):
    def as_numeric(self) -> float:
        global _DISK_WRITE_TS
        _poll_disk_io()
        val = _DISK_IO_CACHE["w_mbs"]
        now = time.monotonic()
        if now - _DISK_WRITE_TS > 0.1:
            _DISK_WRITE_TS = now
            if len(_DISK_WRITE_HIST) != _HIST_SZ:
                _DISK_WRITE_HIST[:] = [math.nan] * _HIST_SZ
            _DISK_WRITE_HIST.append(val)
            _DISK_WRITE_HIST.pop(0)
        return val

    def _raw(self) -> float:
        _poll_disk_io()
        return _DISK_IO_CACHE["w_mbs"]

    def as_string(self) -> str:
        return f"{self._raw():.1f}"

    def last_values(self) -> List[float]:
        return list(_DISK_WRITE_HIST)


# ---------------------------------------------------------------------------
# Power sensors  (GpuPowerW, CpuPowerW)
#
# GpuPowerW: NVIDIA GPU power via pynvml (nvidia-ml-py).
#   Install: pip install nvidia-ml-py
#
# CpuPowerW: AMD CPU Package Power Tracking (PPT) from the amdgpu hwmon
#   driver, which exposes it as power1_input in milliwatts.
# ---------------------------------------------------------------------------

# --- GPU power (pynvml) ---
try:
    import pynvml as _nvml
    _nvml.nvmlInit()
    _NVML_HANDLE = _nvml.nvmlDeviceGetHandleByIndex(0)
    _NVML_OK = True
except Exception:
    _NVML_OK = False
    _NVML_HANDLE = None


class GpuPowerW(CustomDataSource):
    def as_numeric(self) -> float:
        if not _NVML_OK:
            return math.nan
        try:
            return _nvml.nvmlDeviceGetPowerUsage(_NVML_HANDLE) / 1000.0  # mW → W
        except Exception:
            return math.nan

    def as_string(self) -> str:
        v = self.as_numeric()
        return f"{v:.0f} W" if not math.isnan(v) else "N/A"

    def last_values(self) -> List[float]:
        return []


# --- CPU power (amdgpu hwmon PPT) ---
_CPU_POWER_PATH: str = ""
for _hwmon_dir in glob.glob("/sys/class/hwmon/hwmon*/"):
    _name_f = os.path.join(_hwmon_dir, "name")
    if os.path.exists(_name_f):
        with open(_name_f) as _f:
            if _f.read().strip() == "amdgpu":
                _pwr_f = os.path.join(_hwmon_dir, "power1_input")
                if os.path.exists(_pwr_f):
                    _CPU_POWER_PATH = _pwr_f
                    break


class CpuPowerW(CustomDataSource):
    def as_numeric(self) -> float:
        if not _CPU_POWER_PATH:
            return math.nan
        try:
            with open(_CPU_POWER_PATH) as f:
                return int(f.read().strip()) / 1000.0  # mW → W
        except Exception:
            return math.nan

    def as_string(self) -> str:
        v = self.as_numeric()
        return f"{v:.0f} W" if not math.isnan(v) else "N/A"

    def last_values(self) -> List[float]:
        return []


# --- GPU memory in GB (GpuMemUsedGB, GpuMemTotalGB) ---
class GpuMemUsedGB(CustomDataSource):
    def as_numeric(self) -> float:
        if not _NVML_OK:
            return math.nan
        try:
            return _nvml.nvmlDeviceGetMemoryInfo(_NVML_HANDLE).used / 1_073_741_824
        except Exception:
            return math.nan

    def as_string(self) -> str:
        v = self.as_numeric()
        return f"{v:.1f} GB" if not math.isnan(v) else "N/A"

    def last_values(self) -> List[float]:
        return []


class GpuMemTotalGB(CustomDataSource):
    def as_numeric(self) -> float:
        if not _NVML_OK:
            return math.nan
        try:
            return _nvml.nvmlDeviceGetMemoryInfo(_NVML_HANDLE).total / 1_073_741_824
        except Exception:
            return math.nan

    def as_string(self) -> str:
        v = self.as_numeric()
        return f"{v:.1f} GB" if not math.isnan(v) else "N/A"

    def last_values(self) -> List[float]:
        return []
