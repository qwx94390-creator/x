from pathlib import Path

from ops.control_panel import ControlPanelService


def test_save_and_load_full_settings(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "config.yaml").write_text(
        "polymarket:\n  api_url: 'https://a'\n  ws_url: 'wss://b'\n", encoding="utf-8"
    )
    svc = ControlPanelService(repo_root=repo, config_file="config.local.yaml")

    svc.save_settings(
        {
            "api_url": "https://new-api",
            "ws_url": "wss://new-ws",
            "strategy_mode": "trend",
            "trend_lookback": "8",
            "trend_threshold_bps": "60",
            "trend_size": "20",
            "max_order_size": "120",
            "max_position_notional": "600",
            "min_edge_bps": "90",
            "initial_cash_usdt": "30",
            "telegram_token": "t",
            "telegram_chat_id": "c",
            "feishu_webhook_url": "f",
            "llm_provider": "openai_compatible",
            "llm_base_url": "https://example.com/v1/chat/completions",
            "llm_api_key": "k",
            "llm_model": "gpt-x",
        }
    )
    cfg = svc.load_config()

    assert cfg["polymarket"]["api_url"] == "https://new-api"
    assert cfg["strategy"]["mode"] == "trend"
    assert cfg["risk"]["min_edge_bps"] == 90
    assert cfg["portfolio"]["initial_cash_usdt"] == 30.0
    assert cfg["notifications"]["telegram_token"] == "t"
    assert cfg["llm"]["model"] == "gpt-x"


def test_app_status_stopped_when_pid_missing(tmp_path: Path) -> None:
    svc = ControlPanelService(repo_root=tmp_path)
    assert svc.app_status() == "stopped"


def test_latest_cycle_summary_from_log(tmp_path: Path) -> None:
    svc = ControlPanelService(repo_root=tmp_path)
    (tmp_path / "bot.log").write_text(
        "x\n2026-01-01 | INFO | cycle summary: {'fills': 2, 'volume': 8.5}\n", encoding="utf-8"
    )
    summary = svc.latest_cycle_summary()
    assert summary["fills"] == 2
    assert summary["volume"] == 8.5
