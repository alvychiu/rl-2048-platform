"""T-01 骨架冒烟测试：验证包结构可导入、关键第三方依赖存在。

这是项目骨架阶段的最小验证，确保后续任务有可用的工程基座。
"""


def test_src_package_importable():
    import src

    assert src.__version__ == "0.1.0"


def test_subpackages_importable():
    import importlib

    for name in [
        "src.env",
        "src.agents",
        "src.train",
        "src.eval",
        "src.utils",
    ]:
        assert importlib.import_module(name) is not None


def test_core_third_party_available():
    import gymnasium  # noqa: F401
    import numpy  # noqa: F401
    import torch  # noqa: F401
    import yaml  # noqa: F401
