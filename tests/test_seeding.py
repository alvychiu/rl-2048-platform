"""T-02 测试：种子可复现性与设备解析。关联 TC-022, TC-023, TC-024。"""

import random

import numpy as np
import pytest
import torch

from src.utils.seeding import resolve_device, set_global_seed


def test_seed_reproducible_python_numpy_torch():
    set_global_seed(123)
    py1 = [random.random() for _ in range(3)]
    np1 = np.random.rand(3).tolist()
    tr1 = torch.rand(3).tolist()

    set_global_seed(123)
    py2 = [random.random() for _ in range(3)]
    np2 = np.random.rand(3).tolist()
    tr2 = torch.rand(3).tolist()

    assert py1 == py2
    assert np1 == np2
    assert tr1 == tr2


def test_seed_rejects_negative():
    with pytest.raises(ValueError):
        set_global_seed(-1)


def test_resolve_device_cpu():
    assert resolve_device("cpu").type == "cpu"


def test_resolve_device_auto_returns_valid():
    dev = resolve_device("auto")
    assert dev.type in {"cpu", "mps", "cuda"}


def test_resolve_device_cuda_falls_back_when_unavailable():
    # 本环境无 CUDA，应优雅回退到 cpu（TC-022）。
    if not torch.cuda.is_available():
        assert resolve_device("cuda").type == "cpu"


def test_resolve_device_unknown_raises():
    with pytest.raises(ValueError):
        resolve_device("tpu")
