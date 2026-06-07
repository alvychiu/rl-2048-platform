"""T-08 配置加载与校验测试。关联 US-04 / TC-015~TC-018。"""

import os
import stat

import pytest

from src.train.config import Config


def test_tc015_load_valid_quick_yaml():
    cfg = Config.from_yaml("configs/quick.yaml")
    assert cfg.total_steps == 3000
    assert cfg.batch_size == 64
    assert cfg.hidden_sizes == [128, 128]
    assert cfg.device == "auto"


def test_load_full_yaml():
    cfg = Config.from_yaml("configs/full.yaml")
    assert cfg.total_steps == 250000
    assert cfg.run_name == "full"
    assert cfg.reward_empty_coef > 0
    assert cfg.hidden_sizes == [256, 256, 128]


def test_load_full_v5_yaml():
    cfg = Config.from_yaml("configs/full_v5.yaml")
    assert cfg.reward_snake_coef == 4.0
    assert cfg.reward_snake_corner == "bottom-left"
    assert cfg.reward_snake_ratio == 0.7
    assert cfg.discouraged_action == 0
    assert cfg.discouraged_action_penalty == -0.5
    assert cfg.run_name == "full_v5"


def test_load_full_v4_yaml():
    cfg = Config.from_yaml("configs/full_v4.yaml")
    assert cfg.total_steps == 800000
    assert cfg.eps_end == 0.01
    assert cfg.eps_decay_steps == 160000
    assert cfg.reward_milestones[512] == 60.0
    assert cfg.reward_structure_corner_log_scale is False
    assert cfg.reward_structure_corner_min_tile == 128
    assert cfg.reward_high_tile_coef == 0.08
    assert cfg.grad_clip_max_norm == 5.0
    assert cfg.gamma == 0.998
    assert cfg.max_steps == 15000


def test_load_full_v3_smoke_yaml():
    cfg = Config.from_yaml("configs/full_v3_smoke.yaml")
    assert cfg.reward_structure_coef == 1.0
    assert cfg.reward_structure_corner == 2.0
    assert cfg.run_name == "full_v3_smoke"


def test_load_full_v2_smoke_yaml():
    cfg = Config.from_yaml("configs/full_v2_smoke.yaml")
    assert cfg.total_steps == 50000
    assert cfg.merge_reward_scale == 0.05
    assert cfg.reward_milestones[1024] == 80.0
    assert cfg.hidden_sizes == [512, 512, 256]
    assert cfg.gamma == 0.995


def test_tc016_missing_required_field(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("lr: 0.001\n", encoding="utf-8")  # 缺 total_steps
    with pytest.raises(ValueError, match="total_steps"):
        Config.from_yaml(str(p))


def test_tc017_type_error_field():
    with pytest.raises(TypeError, match="lr"):
        Config.from_dict({"total_steps": 1000, "lr": "abc"})


def test_unknown_key_rejected():
    with pytest.raises(ValueError, match="unknown"):
        Config.from_dict({"total_steps": 1000, "foo": 1})


def test_value_range_validation():
    with pytest.raises(ValueError):
        Config.from_dict({"total_steps": 1000, "gamma": 2.0})


def test_tc018_no_read_permission(tmp_path):
    p = tmp_path / "secret.yaml"
    p.write_text("total_steps: 1000\n", encoding="utf-8")
    os.chmod(p, 0)  # 移除所有权限
    try:
        if os.access(str(p), os.R_OK):
            pytest.skip("running as root; permission not enforced")
        with pytest.raises(PermissionError):
            Config.from_yaml(str(p))
    finally:
        os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)


def test_int_not_accept_bool():
    with pytest.raises(TypeError):
        Config.from_dict({"total_steps": True})
