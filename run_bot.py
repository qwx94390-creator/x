import argparse
import asyncio
import sys


def _print_missing_dependency_help(exc: ModuleNotFoundError) -> None:
    missing = exc.name or "unknown"
    msg = (
        f"Missing dependency: {missing}\n"
        "Please install project requirements first:\n"
        "  python -m venv .venv\n"
        "  .venv\\Scripts\\activate    (Windows)\n"
        "  source .venv/bin/activate   (Linux/macOS)\n"
        "  pip install -r requirements.txt\n"
    )
    print(msg, file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()

    try:
        from core.engine import TradingEngine
        from core.service_container import build_services
        from utils.config import load_config
    except ModuleNotFoundError as exc:
        _print_missing_dependency_help(exc)
        raise SystemExit(1) from exc

    config = load_config(args.config)
    services = build_services(config)
    engine = TradingEngine(services)

    async def _run() -> None:
        await engine.setup()
        if args.once:
            await engine.run_once()
        else:
            await engine.run_forever(interval_sec=args.interval)

    asyncio.run(_run())


if __name__ == "__main__":
    main()
