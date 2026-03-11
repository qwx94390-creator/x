import ast
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

    def _save_config(self, config: dict) -> None:
        with self.config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)

    def save_settings(self, form: dict[str, str]) -> None:
        config = self.load_config()

        config.setdefault("polymarket", {})
        config["polymarket"]["api_url"] = form.get("api_url", "").strip()
        config["polymarket"]["ws_url"] = form.get("ws_url", "").strip()

        config.setdefault("strategy", {})
        config["strategy"]["mode"] = form.get("strategy_mode", "hybrid").strip() or "hybrid"
        config["strategy"]["trend_lookback"] = int(form.get("trend_lookback", "5") or 5)
        config["strategy"]["trend_threshold_bps"] = int(form.get("trend_threshold_bps", "50") or 50)
        config["strategy"]["trend_size"] = float(form.get("trend_size", "15") or 15)

        config.setdefault("risk", {})
        config["risk"]["max_order_size"] = float(form.get("max_order_size", "200") or 200)
        config["risk"]["max_position_notional"] = float(form.get("max_position_notional", "1000") or 1000)
        config["risk"]["min_edge_bps"] = int(form.get("min_edge_bps", "80") or 80)

        config.setdefault("portfolio", {})
        config["portfolio"]["initial_cash_usdt"] = float(form.get("initial_cash_usdt", "20") or 20)

        config.setdefault("notifications", {})
        config["notifications"]["telegram_token"] = form.get("telegram_token", "").strip()
        config["notifications"]["telegram_chat_id"] = form.get("telegram_chat_id", "").strip()
        config["notifications"]["feishu_webhook_url"] = form.get("feishu_webhook_url", "").strip()

        config.setdefault("llm", {})
        config["llm"]["provider"] = form.get("llm_provider", "openai_compatible").strip() or "openai_compatible"
        config["llm"]["base_url"] = form.get("llm_base_url", "").strip()
        config["llm"]["api_key"] = form.get("llm_api_key", "").strip()
        config["llm"]["model"] = form.get("llm_model", "").strip()

        self._save_config(config)

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

    def latest_cycle_summary(self) -> dict:
        if not self.log_path.exists():
            return {}
        lines = self.log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in reversed(lines):
            if "cycle summary:" in line:
                raw = line.split("cycle summary:", 1)[1].strip()
                try:
                    obj = ast.literal_eval(raw)
                    if isinstance(obj, dict):
                        return obj
                except Exception:  # noqa: BLE001
                    return {"raw": raw}
        return {}

    def tail_logs(self, n: int = 120) -> str:
        if not self.log_path.exists():
            return "(暂无日志)"
        lines = self.log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(lines[-n:]) if lines else "(暂无日志)"
