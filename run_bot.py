import argparse
import asyncio

from core.engine import TradingEngine
from core.service_container import build_services
from utils.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()

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
