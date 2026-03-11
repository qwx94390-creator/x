from utils.config import load_config


def test_config_contains_conflict_sensitive_keys() -> None:
    cfg = load_config("config.yaml")

    assert "portfolio" in cfg
    assert "initial_cash_usdt" in cfg["portfolio"]

    assert "notifications" in cfg
    assert "feishu_webhook_url" in cfg["notifications"]

    assert "llm" in cfg
    assert "base_url" in cfg["llm"]
    assert "api_key" in cfg["llm"]
    assert "model" in cfg["llm"]
