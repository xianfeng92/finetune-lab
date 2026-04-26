from __future__ import annotations

import json
import platform
import shutil
import sys


def main() -> None:
    payload = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "has_nvidia_smi": shutil.which("nvidia-smi") is not None,
        "has_node": shutil.which("node") is not None,
        "has_npm": shutil.which("npm") is not None,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
