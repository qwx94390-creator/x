# Polymarket Quant Bot (Professional Skeleton)

一个可运行、可扩展的 Polymarket 量化交易机器人骨架项目，包含：

- 实时/轮询市场数据
- 策略引擎（示例：套利）
- 风控引擎
- 执行引擎（Paper Router）
- 组合与 PnL 跟踪
- 数据库落盘（SQLAlchemy）
- 通知接口（Telegram/Feishu）
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
- `notifications/`: Telegram/Feishu/Discord 通知接口
- `backtest/`: 历史回测框架

## 说明

本项目是职业级系统的工程化骨架：
- 已具备完整模块边界与可运行主流程；
- 可直接扩展为多策略、多市场、低延迟执行体系；
- 生产化时请补充：签名认证、重试/熔断、订单状态机、监控告警、CI/CD。


## 通知配置

在 `config.yaml` 的 `notifications` 下可以配置：

- `telegram_token` + `telegram_chat_id`：Telegram 机器人通知
- `feishu_webhook_url`：飞书机器人自定义 Webhook 通知

支持同时配置，系统会并行发送。
