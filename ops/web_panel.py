import html
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from ops.control_panel import ControlPanelService


class PanelHandler(BaseHTTPRequestHandler):
    service = ControlPanelService(Path(__file__).resolve().parents[1])

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self._respond(200, "ok", "text/plain")
            return

        if self.path.startswith("/status"):
            api_ok, api_msg = self.service.check_api_connection()
            data = {
                "api_ok": api_ok,
                "api_message": api_msg,
                "app_status": self.service.app_status(),
                "latest_cycle_summary": self.service.latest_cycle_summary(),
            }
            self._respond(200, json.dumps(data, ensure_ascii=False), "application/json")
            return

        config = self.service.load_config()
        api_ok, api_msg = self.service.check_api_connection()
        status = self.service.app_status()
        summary = self.service.latest_cycle_summary()
        logs = html.escape(self.service.tail_logs())

        polymarket = config.get("polymarket", {})
        strategy = config.get("strategy", {})
        risk = config.get("risk", {})
        portfolio = config.get("portfolio", {})
        notifications = config.get("notifications", {})
        llm = config.get("llm", {})

        html_page = f"""
<!doctype html>
<html lang='zh'>
<head>
  <meta charset='utf-8'/>
  <meta name='viewport' content='width=device-width,initial-scale=1'/>
  <title>交易机器人全功能控制台</title>
  <style>
    :root {{ --bg:#0b1020; --card:#141b34; --line:#243156; --text:#dbe7ff; --muted:#8ea2d8; --ok:#22c55e; --bad:#ef4444; --btn:#3b82f6; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family: Inter, Arial, sans-serif; background:var(--bg); color:var(--text); }}
    .wrap {{ max-width:1200px; margin:0 auto; padding:24px; }}
    .hero {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }}
    .subtitle {{ color:var(--muted); font-size:14px; }}
    .cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:14px; }}
    .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap:14px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px; }}
    .badge {{ padding:4px 10px; border-radius:999px; font-size:12px; display:inline-block; }}
    .ok {{ background:rgba(34,197,94,.16); color:#86efac; }}
    .bad {{ background:rgba(239,68,68,.16); color:#fca5a5; }}
    label {{ display:block; margin-top:10px; color:var(--muted); font-size:13px; }}
    input, select, textarea {{ width:100%; background:#0e1530; border:1px solid var(--line); color:var(--text); border-radius:10px; padding:10px; margin-top:6px; }}
    .actions {{ margin-top:12px; display:flex; gap:8px; flex-wrap:wrap; }}
    button {{ border:0; border-radius:10px; padding:10px 14px; cursor:pointer; font-weight:600; }}
    .primary {{ background:var(--btn); color:white; }}
    .ghost {{ background:transparent; color:var(--text); border:1px solid var(--line); }}
    pre {{ background:#0e1530; border:1px solid var(--line); border-radius:10px; padding:10px; overflow:auto; max-height:280px; }}
    @media (max-width: 980px) {{ .grid, .cards {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='hero'>
      <div>
        <h2 style='margin:0'>交易机器人全功能前端控制台</h2>
        <div class='subtitle'>API、策略、风控、资金、通知、LLM、连接状态、应用状态、日志与摘要全都可见。</div>
      </div>
      <span class='badge {"ok" if status == "running" else "bad"}'>应用 {status}</span>
    </div>

    <div class='cards'>
      <div class='card'>API连接：<span class='badge {"ok" if api_ok else "bad"}'>{"正常" if api_ok else "异常"}</span><div class='subtitle'>{api_msg}</div></div>
      <div class='card'>最近摘要 fills={summary.get('fills','-')} / volume={summary.get('volume','-')} / pnl={summary.get('daily_realized_pnl','-')}</div>
      <div class='card'>运行状态：<span class='badge {"ok" if status == "running" else "bad"}'>{status}</span></div>
    </div>

    <form method='post' action='/save'>
      <div class='grid'>
        <div class='card'>
          <h3 style='margin-top:0'>交易 API 与策略</h3>
          <label>REST API URL</label><input name='api_url' value='{polymarket.get("api_url", "")}' />
          <label>WS URL</label><input name='ws_url' value='{polymarket.get("ws_url", "")}' />
          <label>策略模式</label>
          <select name='strategy_mode'>
            <option value='hybrid' {'selected' if strategy.get('mode','hybrid') == 'hybrid' else ''}>hybrid（推荐）</option>
            <option value='arbitrage' {'selected' if strategy.get('mode','') == 'arbitrage' else ''}>arbitrage</option>
            <option value='trend' {'selected' if strategy.get('mode','') == 'trend' else ''}>trend</option>
          </select>
          <label>trend_lookback</label><input name='trend_lookback' value='{strategy.get("trend_lookback", 5)}' />
          <label>trend_threshold_bps</label><input name='trend_threshold_bps' value='{strategy.get("trend_threshold_bps", 50)}' />
          <label>trend_size</label><input name='trend_size' value='{strategy.get("trend_size", 15.0)}' />
        </div>

        <div class='card'>
          <h3 style='margin-top:0'>风控与资金</h3>
          <label>max_order_size</label><input name='max_order_size' value='{risk.get("max_order_size", 200)}' />
          <label>max_position_notional</label><input name='max_position_notional' value='{risk.get("max_position_notional", 1000)}' />
          <label>min_edge_bps</label><input name='min_edge_bps' value='{risk.get("min_edge_bps", 80)}' />
          <label>initial_cash_usdt</label><input name='initial_cash_usdt' value='{portfolio.get("initial_cash_usdt", 20)}' />
        </div>

        <div class='card'>
          <h3 style='margin-top:0'>通知</h3>
          <label>telegram_token</label><input name='telegram_token' value='{notifications.get("telegram_token", "")}' />
          <label>telegram_chat_id</label><input name='telegram_chat_id' value='{notifications.get("telegram_chat_id", "")}' />
          <label>feishu_webhook_url</label><input name='feishu_webhook_url' value='{notifications.get("feishu_webhook_url", "")}' />
        </div>

        <div class='card'>
          <h3 style='margin-top:0'>LLM 诊断</h3>
          <label>llm_provider</label><input name='llm_provider' value='{llm.get("provider", "openai_compatible")}' />
          <label>llm_base_url</label><input name='llm_base_url' value='{llm.get("base_url", "")}' />
          <label>llm_api_key</label><input name='llm_api_key' value='{llm.get("api_key", "")}' />
          <label>llm_model</label><input name='llm_model' value='{llm.get("model", "")}' />
        </div>
      </div>

      <div class='actions'>
        <button class='primary' type='submit'>保存全部设置</button>
        <button class='ghost' formaction='/check' formmethod='post'>刷新连接检测</button>
      </div>
    </form>

    <div class='actions' style='margin-top:10px'>
      <form method='post' action='/start'><button class='primary' type='submit'>启动应用</button></form>
      <form method='post' action='/stop'><button class='ghost' type='submit'>停止应用</button></form>
    </div>

    <div class='card' style='margin-top:14px'>
      <h3 style='margin-top:0'>运行日志（尾部）</h3>
      <pre>{logs}</pre>
    </div>
  </div>
</body>
</html>
"""
        self._respond(200, html_page)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(data)
        flat = {k: v[0] if v else "" for k, v in form.items()}

        if self.path == "/save":
            self.service.save_settings(flat)
        elif self.path == "/start":
            self.service.start_app()
        elif self.path == "/stop":
            self.service.stop_app()
        elif self.path == "/check":
            pass

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def _respond(self, code: int, body: str, content_type: str = "text/html") -> None:
        encoded = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_server(port: int = 8080) -> None:
    server = HTTPServer(("0.0.0.0", port), PanelHandler)
    print(f"Control panel running on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
