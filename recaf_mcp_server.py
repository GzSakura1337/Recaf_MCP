#!/usr/bin/env python3

from pathlib import Path
import runpy
import sys


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    server_dir = root / "mcp-server"
    sys.path.insert(0, str(server_dir))
    target = server_dir / "recaf_mcp_server.py"
    runpy.run_path(str(target), run_name="__main__")
