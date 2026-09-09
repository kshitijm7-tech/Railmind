"""RailMind railway-demo seed package.

Canonical synthetic operational dataset (``data/railway_demo/``) loading and
adaptation layer. See ``data/railway_demo/README.md``.
"""

from app.infrastructure.railway_demo.loader import get_demo_dataset, DemoDataset
from app.infrastructure.railway_demo.repository import (
    OperationalRepository,
    DemoSeedRepository,
    get_demo_seed_repository,
)

__all__ = [
    "DemoDataset",
    "DemoSeedRepository",
    "OperationalRepository",
    "get_demo_dataset",
    "get_demo_seed_repository",
]
