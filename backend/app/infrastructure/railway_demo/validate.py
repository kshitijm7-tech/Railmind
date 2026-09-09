"""Consistency validation for the railway-demo dataset (spec §15)."""

from __future__ import annotations

from datetime import datetime
from typing import List

from app.infrastructure.railway_demo.loader import DemoDataset


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value)


def validate_dataset(dataset: DemoDataset) -> List[str]:
    errors: List[str] = []
    station_ids = {s["station_id"] for s in dataset.stations}
    section_ids = {s["section_id"] for s in dataset.sections}
    train_ids = {t["train_id"] for t in dataset.trains}

    for section in dataset.sections:
        for key in ("from_station_id", "to_station_id"):
            if section[key] not in station_ids:
                errors.append(
                    f"Section {section['section_id']}: unknown station {section[key]}"
                )

    for train in dataset.trains:
        if train["origin_station_id"] not in station_ids:
            errors.append(f"Train {train['train_id']}: unknown origin {train['origin_station_id']}")
        if train["destination_station_id"] not in station_ids:
            errors.append(
                f"Train {train['train_id']}: unknown destination {train['destination_station_id']}"
            )
        for section_id in train.get("route", []):
            if section_id not in section_ids:
                errors.append(f"Train {train['train_id']}: unknown route section {section_id}")
        if train.get("current_section_id") and train["current_section_id"] not in section_ids:
            errors.append(
                f"Train {train['train_id']}: unknown current section {train['current_section_id']}"
            )

    for movement in dataset.train_movements:
        if movement["train_id"] not in train_ids:
            errors.append(f"Movement {movement['movement_id']}: unknown train {movement['train_id']}")
        if movement["section_id"] not in section_ids:
            errors.append(
                f"Movement {movement['movement_id']}: unknown section {movement['section_id']}"
            )
        if not _parse(movement["entry_time"]) < _parse(movement["exit_time"]):
            errors.append(f"Movement {movement['movement_id']}: entry_time >= exit_time")

    for task in dataset.maintenance_tasks:
        if task["section_id"] not in section_ids:
            errors.append(f"Task {task['task_id']}: unknown section {task['section_id']}")
        if not _parse(task["earliest_start"]) < _parse(task["latest_finish"]):
            errors.append(f"Task {task['task_id']}: earliest_start >= latest_finish")

    for asset in dataset.assets:
        if asset["section_id"] not in section_ids:
            errors.append(f"Asset {asset['asset_id']}: unknown section {asset['section_id']}")

    for disruption in dataset.disruptions:
        if disruption["section_id"] not in section_ids:
            errors.append(
                f"Disruption {disruption['scenario_id']}: unknown section {disruption['section_id']}"
            )

    return errors


EXPECTED_COUNTS = {
    "stations": 6,
    "sections": 8,
    "trains": 12,
    "train_movements": 3,
    "assets": 5,
    "maintenance_tasks": 5,
    "disruptions": 2,
}


def check_counts(dataset: DemoDataset) -> List[str]:
    errors: List[str] = []
    actual = {
        "stations": len(dataset.stations),
        "sections": len(dataset.sections),
        "trains": len(dataset.trains),
        "train_movements": len(dataset.train_movements),
        "assets": len(dataset.assets),
        "maintenance_tasks": len(dataset.maintenance_tasks),
        "disruptions": len(dataset.disruptions),
    }
    for key, expected in EXPECTED_COUNTS.items():
        if actual[key] != expected:
            errors.append(f"Count mismatch for {key}: expected {expected}, got {actual[key]}")
    return errors
