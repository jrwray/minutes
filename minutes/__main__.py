"""Entry point: python -m minutes [--port 7860] [--no-browser]"""

import argparse
import logging
import sys
import threading
import warnings
import webbrowser

warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def utf8_console() -> None:
    """Windows consoles default to a legacy code page (cp1252) that can't encode
    characters like '→' or names in other scripts; printing or logging them would
    raise. Switch our streams to UTF-8 and never fail on an unencodable character."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    utf8_console()
    parser = argparse.ArgumentParser(prog="minutes")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    import uvicorn

    url = f"http://127.0.0.1:{args.port}"
    print(f"\n  Minutes is running at {url}\n  Close this window to stop it.\n")
    if not args.no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    uvicorn.run("minutes.server:app", host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
