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
            }
            self._respond(200, json.dumps(data, ensure_ascii=False), "application/json")
            return

        config = self.service.load_config()
        api_url = config.get("polymarket", {}).get("api_url", "")
        ws_url = config.get("polymarket", {}).get("ws_url", "")
        strategy_mode = config.get("strategy", {}).get("mode", "hybrid")
        api_ok, api_msg = self.service.check_api_connection()
        status = self.service.app_status()

        html = f"""
<!doctype html>
<html lang='zh'>
<head>
  <meta charset='utf-8'/>
  <meta name='viewport' content='width=device-width,initial-scale=1'/>
  <title>交易机器人控制台</title>
  <style>
    :root {{ --bg:#0b1020; --card:#141b34; --line:#243156; --text:#dbe7ff; --muted:#8ea2d8; --ok:#22c55e; --bad:#ef4444; --btn:#3b82f6; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family: Inter, Arial, sans-serif; background:var(--bg); color:var(--text); }}
    .wrap {{ max-width:1100px; margin:0 auto; padding:24px; }}
    .hero {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }}
    .subtitle {{ color:var(--muted); font-size:14px; }}
    .grid {{ display:grid; grid-template-columns: 1.2fr 1fr; gap:14px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px; }}
    .badge {{ padding:4px 10px; border-radius:999px; font-size:12px; display:inline-block; }}
    .ok {{ background:rgba(34,197,94,.16); color:#86efac; }}
    .bad {{ background:rgba(239,68,68,.16); color:#fca5a5; }}
    label {{ display:block; margin-top:10px; color:var(--muted); font-size:13px; }}
    input, select {{ width:100%; background:#0e1530; border:1px solid var(--line); color:var(--text); border-radius:10px; padding:10px; margin-top:6px; }}
    .actions {{ margin-top:12px; display:flex; gap:8px; flex-wrap:wrap; }}
    button {{ border:0; border-radius:10px; padding:10px 14px; cursor:pointer; font-weight:600; }}
    .primary {{ background:var(--btn); color:white; }}
    .ghost {{ background:transparent; color:var(--text); border:1px solid var(--line); }}
    .tips li {{ color:var(--muted); margin:8px 0; }}
    @media (max-width: 880px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='hero'>
      <div>
        <h2 style='margin:0'>交易机器人前端控制台</h2>
        <div class='subtitle'>借鉴优秀交易控制台设计：卡片化信息分区、状态徽章、主次按钮、关键状态首屏可见。</div>
      </div>
      <div>
        <span class='badge {"ok" if status == "running" else "bad"}'>应用 {status}</span>
      </div>
    </div>

    <div class='grid'>
      <div class='card'>
        <h3 style='margin-top:0'>接口与策略设置</h3>
        <form method='post' action='/save'>
          <label>REST API URL</label>
          <input name='api_url' value='{api_url}' />
          <label>WS URL</label>
          <input name='ws_url' value='{ws_url}' />
          <label>策略模式</label>
          <select name='strategy_mode'>
            <option value='hybrid' {'selected' if strategy_mode == 'hybrid' else ''}>hybrid（推荐）</option>
            <option value='arbitrage' {'selected' if strategy_mode == 'arbitrage' else ''}>arbitrage</option>
            <option value='trend' {'selected' if strategy_mode == 'trend' else ''}>trend</option>
          </select>
          <div class='actions'>
            <button class='primary' type='submit'>保存设置</button>
            <button class='ghost' formaction='/check' formmethod='post'>刷新连接检测</button>
          </div>
        </form>
      </div>

      <div class='card'>
        <h3 style='margin-top:0'>运行状态</h3>
        <p>API连接状态：<span class='badge {"ok" if api_ok else "bad"}'>{"正常" if api_ok else "异常"}</span></p>
        <p style='color:var(--muted); margin-top:-4px'>检测结果：{api_msg}</p>
        <p>应用运行状态：<span class='badge {"ok" if status == "running" else "bad"}'>{status}</span></p>
        <div class='actions'>
          <form method='post' action='/start'><button class='primary' type='submit'>启动应用</button></form>
          <form method='post' action='/stop'><button class='ghost' type='submit'>停止应用</button></form>
        </div>
      </div>
    </div>

    <div class='card' style='margin-top:14px'>
      <h3 style='margin-top:0'>设计与操作优化建议（已内置）</h3>
      <ul class='tips'>
        <li>首屏展示连接与运行状态，降低排障路径。</li>
        <li>把“保存设置”和“启动/停止”分区，减少误操作。</li>
        <li>策略模式可视化切换（hybrid/arbitrage/trend），方便试验。</li>
      </ul>
    </div>
  </div>
</body>
</html>
"""
        self._respond(200, html)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(data)

        if self.path == "/save":
            api_url = form.get("api_url", [""])[0]
            ws_url = form.get("ws_url", [""])[0]
            strategy_mode = form.get("strategy_mode", ["hybrid"])[0]
            self.service.save_api_settings(api_url, ws_url, strategy_mode)
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
