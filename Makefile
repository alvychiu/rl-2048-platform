# 2048 RL 训练实验平台 — 一键入口
# 用法见 `make help`

PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
CONFIG ?= configs/quick.yaml
CKPT ?=
PORT ?= 6006
LOGDIR ?= runs

.PHONY: help venv install train eval board play test clean

help:
	@echo "2048 RL 训练实验平台"
	@echo "--------------------------------------------------"
	@echo "make install              创建 venv 并安装依赖(固定版本)"
	@echo "make train                训练 (默认 $(CONFIG))"
	@echo "make train CONFIG=configs/full.yaml"
	@echo "make train CONFIG=configs/full_v2_smoke.yaml  # 调参烟雾(50k)"
	@echo "make train CONFIG=configs/full_v2.yaml         # 调参完整(600k)"
	@echo "make train CONFIG=configs/full_v3_smoke.yaml   # 结构奖励烟雾(50k)"
	@echo "make train CONFIG=configs/full_v3.yaml         # 结构奖励完整(600k)"
	@echo "make train CONFIG=configs/full_v4_smoke.yaml   # v4烟雾(50k)"
	@echo "make train CONFIG=configs/full_v4.yaml         # v4完整(800k)"
	@echo "make board                启动 TensorBoard (localhost:$(PORT))"
	@echo "make eval CKPT=runs/<id>/best.pt"
	@echo "make play                 启动 2048 GUI（手动游玩）"
	@echo "make play CKPT=runs/<id>/best.pt   AI 自动演示"
	@echo "make test                 运行测试套件"
	@echo "make clean                清理缓存与实验产物"

venv:
	python3 -m venv .venv

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

train:
	$(PYTHON) -m src.train.train --config $(CONFIG)

eval:
	@if [ -z "$(CKPT)" ]; then echo "用法: make eval CKPT=runs/<id>/best.pt [HIDDEN='256 256']"; exit 1; fi
	$(PYTHON) -m src.eval.evaluate --ckpt $(CKPT) $(if $(HIDDEN),--hidden $(HIDDEN),)

board:
	$(PYTHON) -m tensorboard.main --logdir $(LOGDIR) --port $(PORT)

play:
	$(PYTHON) -m src.gui.play $(if $(CKPT),--ckpt $(CKPT),)

test:
	$(PYTHON) -m pytest -q

clean:
	rm -rf .pytest_cache **/__pycache__ src/**/__pycache__ tests/__pycache__
	@echo "如需清理实验产物：rm -rf runs/"
