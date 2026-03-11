from pathlib import Path

from ops.control_panel import ControlPanelService


def test_save_and_load_api_settings(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "config.yaml").write_text(
        "polymarket:\n  api_url: 'https://a'\n  ws_url: 'wss://b'\n", encoding="utf-8"
    )
    svc = ControlPanelService(repo_root=repo, config_file="config.local.yaml")
    cfg = svc.load_config()
    assert cfg["polymarket"]["api_url"] == "https://a"

    svc.save_api_settings("https://new-api", "wss://new-ws")
    cfg2 = svc.load_config()
    assert cfg2["polymarket"]["api_url"] == "https://new-api"
    assert cfg2["polymarket"]["ws_url"] == "wss://new-ws"


def test_app_status_stopped_when_pid_missing(tmp_path: Path) -> None:
    svc = ControlPanelService(repo_root=tmp_path)
    assert svc.app_status() == "stopped"
