# Polymarket Quant Bot (Professional Skeleton)

一个可运行、可扩展的 Polymarket 量化交易机器人骨架项目，包含：

- 实时/轮询市场数据
- 策略引擎（示例：套利）
- 风控引擎
- 执行引擎（Paper Router）
- 组合与 PnL 跟踪
- 数据库落盘（SQLAlchemy）
- 通知接口（Telegram）
- 回测引擎

## 快速启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_bot.py --config config.yaml --once
```

> 默认是 `paper` 模式，不会真实下单。

## 架构

- `core/`: 主引擎、事件总线、调度与容器
- `data/`: REST/WS 数据接入、订单簿聚合
- `strategies/`: 可插拔策略
- `risk/`: 订单级与组合级风控
- `execution/`: 订单路由与执行
- `portfolio/`: 持仓、余额与 PnL
- `database/`: 交易记录和事件
- `notifications/`: Telegram/Discord 通知接口
- `backtest/`: 历史回测框架

## 说明

本项目是职业级系统的工程化骨架：
- 已具备完整模块边界与可运行主流程；
- 可直接扩展为多策略、多市场、低延迟执行体系；
- 生产化时请补充：签名认证、重试/熔断、订单状态机、监控告警、CI/CD。

## 无依赖试跑

在当前仓库中，`run_bot.py --once` 可在纯 Python 标准库环境运行（会在网络不可用时自动回退到内置 demo 市场数据）。
该章节为主线合并后的保留内容，用于避免 README 冲突重复片段。
