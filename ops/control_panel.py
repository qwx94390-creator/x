import subprocess
from pathlib import Path

import httpx
import yaml


class ControlPanelService:
    def __init__(self, repo_root: Path, config_file: str = "config.local.yaml") -> None:
        self.repo_root = repo_root
        self.config_path = repo_root / config_file
        self.pid_path = repo_root / ".bot.pid"
        self.log_path = repo_root / "bot.log"

    def load_config(self) -> dict:
        if not self.config_path.exists():
            default = self.repo_root / "config.yaml"
            if default.exists():
                self.config_path.write_text(default.read_text(encoding="utf-8"), encoding="utf-8")
        with self.config_path.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save_api_settings(self, api_url: str, ws_url: str, strategy_mode: str = "hybrid") -> None:
        config = self.load_config()
        config.setdefault("polymarket", {})
        config["polymarket"]["api_url"] = api_url.strip()
        config["polymarket"]["ws_url"] = ws_url.strip()
        config.setdefault("strategy", {})
        config["strategy"]["mode"] = strategy_mode.strip() or "hybrid"
        with self.config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)

    def check_api_connection(self) -> tuple[bool, str]:
        config = self.load_config()
        api_url = config.get("polymarket", {}).get("api_url", "")
        if not api_url:
            return False, "未配置 polymarket.api_url"
        try:
            resp = httpx.get(f"{api_url}/markets", params={"limit": 1}, timeout=8)
            ok = resp.status_code < 400
            return ok, f"HTTP {resp.status_code}"
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def app_status(self) -> str:
        if not self.pid_path.exists():
            return "stopped"
        try:
            pid = int(self.pid_path.read_text(encoding="utf-8").strip())
            proc = subprocess.run(["ps", "-p", str(pid), "-o", "pid="], capture_output=True, text=True)
            return "running" if proc.stdout.strip() else "stopped"
        except Exception:  # noqa: BLE001
            return "stopped"

    def start_app(self) -> str:
        if self.app_status() == "running":
            return "应用已在运行"
        cmd = ["python", "run_bot.py", "--config", str(self.config_path), "--interval", "5"]
        with self.log_path.open("a", encoding="utf-8") as logf:
            proc = subprocess.Popen(cmd, cwd=self.repo_root, stdout=logf, stderr=logf)  # noqa: S603
        self.pid_path.write_text(str(proc.pid), encoding="utf-8")
        return f"应用已启动，PID={proc.pid}"

    def stop_app(self) -> str:
        if not self.pid_path.exists():
            return "应用未运行"
        pid = int(self.pid_path.read_text(encoding="utf-8").strip())
        subprocess.run(["kill", str(pid)], check=False)
        self.pid_path.unlink(missing_ok=True)
        return f"已停止应用 PID={pid}"
