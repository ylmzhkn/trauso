"""Command-line entry point."""
import argparse
import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(prog="multi-agent")
    parser.add_argument("command", choices=["serve", "tui"], nargs="?", default="serve")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--api-url", default="http://127.0.0.1:8787")
    args = parser.parse_args()
    if args.command == "tui":
        from .tui import run_tui
        run_tui(args.api_url)
        return
    uvicorn.run("multi_agent_plugin.api:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
