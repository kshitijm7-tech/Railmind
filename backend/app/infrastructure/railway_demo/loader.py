"""Loader for the canonical synthetic railway-demo dataset.

The dataset lives at ``<repo-root>/data/railway_demo/`` and is the single
source of truth for stations, sections, trains, movements, assets,
maintenance tasks and disruption scenarios used by the frontend, backend
APIs, E09 planner, E05 simulation, P17 intelligence and P18 recovery.

SYNTHETIC DATA: see ``data/railway_demo/README.md``. Nothing here represents
live Indian Railways operations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


def find_dataset_dir() -> Path:
    """Locate ``data/railway_demo`` from anywhere inside the repo."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / "data" / "railway_demo"
        if candidate.is_dir():
            return candidate
        # Backend package lives at <root>/backend/app/... so also check
        # the grand-parent layout explicitly.
        if parent.name == "backend":
            candidate = parent.parent / "data" / "railway_demo"
            if candidate.is_dir():
                return candidate
    raise FileNotFoundError(
        "Could not locate data/railway_demo from " + str(here)
    )


@dataclass
class DemoDataset:
    corridor: Dict[str, Any]
    stations: List[Dict[str, Any]] = field(default_factory=list)
    sections: List[Dict[str, Any]] = field(default_factory=list)
    trains: List[Dict[str, Any]] = field(default_factory=list)
    train_movements: List[Dict[str, Any]] = field(default_factory=list)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    maintenance_tasks: List[Dict[str, Any]] = field(default_factory=list)
    disruptions: List[Dict[str, Any]] = field(default_factory=list)


def _read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_dataset(dataset_dir: Path | None = None) -> DemoDataset:
    base = Path(dataset_dir) if dataset_dir else find_dataset_dir()
    return DemoDataset(
        corridor=_read_json(base / "corridor.json"),
        stations=_read_json(base / "stations.json"),
        sections=_read_json(base / "sections.json"),
        trains=_read_json(base / "trains.json"),
        train_movements=_read_json(base / "train_movements.json"),
        assets=_read_json(base / "assets.json"),
        maintenance_tasks=_read_json(base / "maintenance_tasks.json"),
        disruptions=_read_json(base / "disruptions.json"),
    )


@lru_cache(maxsize=1)
def get_demo_dataset() -> DemoDataset:
    """Cached singleton: the process-wide canonical demo dataset."""
    return load_dataset()
