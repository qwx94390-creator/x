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
        config = self.service.load_config()
        api_url = config.get("polymarket", {}).get("api_url", "")
        ws_url = config.get("polymarket", {}).get("ws_url", "")
        api_ok, api_msg = self.service.check_api_connection()
        status = self.service.app_status()
        html = f"""
<!doctype html>
<html lang='zh'>
<head>
  <meta charset='utf-8'/>
  <title>交易机器人控制台</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 30px auto; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
    .ok {{ color: #0a7f2e; }}
    .bad {{ color: #b42318; }}
    input {{ width: 100%; padding: 8px; margin: 6px 0 12px; }}
    button {{ padding: 8px 12px; margin-right: 8px; }}
  </style>
</head>
<body>
  <h2>交易机器人前端控制台</h2>
  <div class='card'>
    <h3>API 接口设置</h3>
    <form method='post' action='/save'>
      <label>REST API URL</label>
      <input name='api_url' value='{api_url}' />
      <label>WS URL</label>
      <input name='ws_url' value='{ws_url}' />
      <button type='submit'>保存设置</button>
    </form>
  </div>

  <div class='card'>
    <h3>连接与运行状态</h3>
    <p>API连接状态: <b class='{"ok" if api_ok else "bad"}'>{"正常" if api_ok else "异常"}</b>（{api_msg}）</p>
    <p>应用运行状态: <b class='{"ok" if status == "running" else "bad"}'>{status}</b></p>
    <form method='post' action='/start' style='display:inline'>
      <button type='submit'>启动应用</button>
    </form>
    <form method='post' action='/stop' style='display:inline'>
      <button type='submit'>停止应用</button>
    </form>
    <form method='post' action='/check' style='display:inline'>
      <button type='submit'>刷新连接检测</button>
    </form>
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
            self.service.save_api_settings(api_url, ws_url)
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
