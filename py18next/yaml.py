from pathlib import Path

import yaml

with Path("translation.yaml").open(encoding="utf8") as f:
    data = yaml.safe_load(f)
