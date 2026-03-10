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


## 本地运行（开发调试）

如果你只是想先在本机跑通，按下面步骤即可：

### 1) 准备环境

- Python 3.10+
- 可访问外网（用于拉取市场数据与发送通知）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) 准备配置

```bash
cp config.yaml config.local.yaml
```

然后编辑 `config.local.yaml`，至少确认：

- `app.mode: paper`
- `database.url` 指向本地可写路径
- 通知配置按需填写：
  - `notifications.feishu_webhook_url`
  - 或 `notifications.telegram_token` + `notifications.telegram_chat_id`

### 3) 单次运行（推荐先验证）

```bash
python run_bot.py --config config.local.yaml --once
```

看到 `cycle done` 日志，且通知渠道收到消息（如已配置）即表示跑通。

### 4) 持续运行

```bash
python run_bot.py --config config.local.yaml --interval 5
```

说明：`--interval 5` 表示每 5 秒执行一轮。

### 5) 运行测试

```bash
pytest -q
```


## 云端部署（推荐：Ubuntu + systemd）

下面以常见云服务器（阿里云/腾讯云/AWS EC2）上的 Ubuntu 22.04 为例：

### 1) 准备服务器

```bash
sudo apt update
sudo apt install -y python3 python3-venv git
```

### 2) 拉取代码并安装依赖

```bash
git clone <你的仓库地址> /opt/polymarket-bot
cd /opt/polymarket-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) 配置参数

复制并编辑配置文件（至少填好飞书或 Telegram 其中一个通知）：

```bash
cp config.yaml config.prod.yaml
nano config.prod.yaml
```

建议重点检查：
- `app.mode` 是否为 `paper`
- `database.url` 的路径是否可写
- `notifications.feishu_webhook_url` / `telegram_token` / `telegram_chat_id`

### 4) 先做一次手动验证

```bash
source .venv/bin/activate
python run_bot.py --config config.prod.yaml --once
```

### 5) 配置 systemd 常驻进程

创建 `/etc/systemd/system/polymarket-bot.service`：

```ini
[Unit]
Description=Polymarket Quant Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/polymarket-bot
ExecStart=/opt/polymarket-bot/.venv/bin/python /opt/polymarket-bot/run_bot.py --config /opt/polymarket-bot/config.prod.yaml --interval 5
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

加载并启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable polymarket-bot
sudo systemctl start polymarket-bot
sudo systemctl status polymarket-bot
```

查看实时日志：

```bash
journalctl -u polymarket-bot -f
```

### 6) 更新发布流程

```bash
cd /opt/polymarket-bot
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart polymarket-bot
```

## Docker 部署（可选）

如果你希望容器化运行，可先在仓库中补充 `Dockerfile` 与 `docker-compose.yml`，再通过以下方式启动：

```bash
docker compose up -d
```

当前仓库尚未内置 Docker 编排文件，推荐先使用上面的 `systemd` 方案，稳定后再容器化。
