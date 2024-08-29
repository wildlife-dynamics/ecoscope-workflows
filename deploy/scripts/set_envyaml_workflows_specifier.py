import sys
import copy
from pathlib import Path

import yaml

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: set_environment_workflows_specifier.py <src_envyaml_path> <dst_envyaml_path> <rev>"
        )
        sys.exit(1)

    src_envyaml, dst_envyaml, rev = (
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        sys.argv[3].strip(),
    )

    if not src_envyaml.exists():
        print(f"File {src_envyaml} does not exist")
        sys.exit(1)

    if dst_envyaml.exists():
        print(f"File {dst_envyaml} already exists, exiting")
        sys.exit(1)

    with src_envyaml.open() as f:
        original_env = yaml.safe_load(f)

    new_env: dict[str, list[str]] = copy.deepcopy(original_env)
    for i, dep in enumerate(new_env["dependencies"]):
        if dep.startswith("ecoscope-workflows"):
            new_env["dependencies"][i] = f"ecoscope-workflows=={rev}"
            break

    if len(dst_envyaml.parts) > 1:
        dst_envyaml.parent.mkdir(parents=True, exist_ok=True)
    with dst_envyaml.open("w") as f:
        yaml.dump(new_env, f, sort_keys=False)
