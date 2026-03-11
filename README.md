# Polymarket Quant Bot (Professional Skeleton)

一个可运行、可扩展的 Polymarket 量化交易机器人骨架项目，包含：

- 实时/轮询市场数据
- 策略引擎（示例：套利）
- 风控引擎
- 执行引擎（Paper Router）
- 组合与 PnL 跟踪
- 数据库落盘（SQLAlchemy）
- 通知接口（Telegram/Feishu）
- 每日收益报告与盈亏原因分析
- 大模型诊断与策略参数建议
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

此外支持每日收益诊断：
- 每日推送 PnL/成交量/信号与拒单统计
- 自动分析盈利与亏损原因
- 基于日报调用大模型给出优化建议




### LLM 诊断配置

在 `config.yaml` 里配置 `llm` 段即可启用大模型日报诊断：

- `llm.base_url`：OpenAI 兼容聊天接口地址（如 `/v1/chat/completions`）
- `llm.api_key`：API Key
- `llm.model`：模型名

未配置时系统会自动降级为本地规则分析，不影响主流程。
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
- `portfolio.initial_cash_usdt: 20.0`（初始资金，单位 USDT）
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

每日报告后会根据当日 PnL 自动微调 `risk.min_edge_bps`：
- 当日亏损：提高阈值（更保守）
- 当日盈利：降低阈值（更积极）



### 常见问题（Windows）

如果本地启动报错：`ModuleNotFoundError: No module named 'httpx'` / `sqlalchemy` / `aiosqlite`，说明依赖还没安装到当前 Python 环境。

按下面步骤执行：

```powershell
cd D:\x-main
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_bot.py --config config.yaml --once
```

如果只缺单个包，也可以先快速补：

```powershell
pip install aiosqlite
```

如果你用了 PyCharm/VSCode，请确认解释器选择的是项目内 `.venv`，而不是系统 Python。

### 5) 运行测试

```bash
pytest -q
```






## 策略扩展（新增）

现在支持三种策略模式（可在前端控制台切换）：

- `arbitrage`：仅套利策略
- `trend`：趋势跟随策略（新增）
- `hybrid`：套利 + 趋势组合（默认）

可在 `config.yaml` 的 `strategy` 段配置趋势参数：

- `trend_lookback`
- `trend_threshold_bps`
- `trend_size`

## 前端控制台（简化操作流程）

借鉴优秀交易控制台设计（信息层级清晰、状态一眼可见、关键操作按钮突出、减少页面跳转）。

新增本地 Web 控制台，用于：

- 设置交易 API 接口（REST/WS）
- 查看 API 连接状态
- 查看应用运行状态（running/stopped）
- 一键启动/停止机器人

启动方式：

```bash
bash scripts/run_panel.sh
```

打开浏览器访问：`http://127.0.0.1:8080`

## 打包下载到本地

如果你想把当前项目打包后下载到本地电脑，可以这样做：

### 1) 在服务器上执行打包脚本

```bash
bash scripts/package_release.sh
```

默认会在 `dist/` 下生成类似：

- `dist/polymarket-bot-YYYYMMDD-HHMMSS.tar.gz`

压缩包内已包含顶层目录 `polymarket-bot-<version>/`，解压后不会把文件散落到当前目录。

你也可以自定义版本号：

```bash
bash scripts/package_release.sh v1.0.0
```

### 2) 下载到本地

在**本地电脑**执行（将 IP 替换为你的云服务器公网地址）：

```bash
scp ubuntu@<server-ip>:/opt/polymarket-bot/dist/polymarket-bot-*.tar.gz .
```

### 3) 本地解压

```bash
tar -xzf polymarket-bot-*.tar.gz
cd polymarket-bot-*
```

### 4) 一键本地运行

```bash
bash scripts/run_local.sh
```

该脚本会自动创建虚拟环境、安装依赖、生成 `config.local.yaml`（若不存在），并执行一次 `--once` 验证。

说明：打包时会自动排除 `.venv`、`.git`、`__pycache__`、`.pytest_cache`、`dist` 等临时/本地文件。


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
- `portfolio.initial_cash_usdt` 是否符合你的实盘/模拟资金规模
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


## 冲突处理说明

如果你在 GitHub 上看到 `README.md`、`config.yaml`、`core/service_container.py` 冲突，建议按下面顺序处理：

1. 保留 `README.md` 中“本地运行 / 打包下载 / 云端部署 / LLM 诊断配置”章节；
2. 保留 `config.yaml` 中 `portfolio.initial_cash_usdt`、`notifications.feishu_webhook_url`、`llm.*` 三组配置；
3. 保留 `core/service_container.py` 中 `MultiNotifier + FeishuNotifier + TelegramNotifier` 组合，且 `Services` 包含 `reporter` 和 `advisor`；
4. 运行 `pytest -q` 验证后再推送。
