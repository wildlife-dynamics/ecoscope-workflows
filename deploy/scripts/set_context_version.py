import sys
import copy
from pathlib import Path

import yaml

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: set_context_version.py <src> <dst> <version>")
        sys.exit(1)

    src, dst, version = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].strip()

    if not src.exists():
        print(f"File {src} does not exist")
        sys.exit(1)

    if dst.exists():
        print(f"File {dst} already exists, exiting")
        sys.exit(1)

    with src.open() as f:
        original = yaml.safe_load(f)

    new = copy.deepcopy(original)
    new["context"]["version"] = version

    if len(dst.parts) > 1:
        dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w") as f:
        yaml.dump(new, f, sort_keys=False)
