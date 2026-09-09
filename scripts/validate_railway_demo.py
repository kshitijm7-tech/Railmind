"""Validate the canonical railway-demo dataset (spec §15 + §16 counts).

Usage (from repo root)::

    python scripts/validate_railway_demo.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.infrastructure.railway_demo.loader import load_dataset  # noqa: E402
from app.infrastructure.railway_demo.validate import (  # noqa: E402
    check_counts,
    validate_dataset,
)


def main() -> int:
    dataset = load_dataset()
    errors = validate_dataset(dataset) + check_counts(dataset)
    print(f"stations:          {len(dataset.stations)}")
    print(f"sections:          {len(dataset.sections)}")
    print(f"trains:            {len(dataset.trains)}")
    print(f"train_movements:   {len(dataset.train_movements)}")
    print(f"assets:            {len(dataset.assets)}")
    print(f"maintenance_tasks: {len(dataset.maintenance_tasks)}")
    print(f"disruptions:       {len(dataset.disruptions)}")
    if errors:
        print("\nVALIDATION FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("\nValidation passed: referential integrity, time ordering and counts OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
