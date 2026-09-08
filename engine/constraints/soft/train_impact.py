"""SOFT — Train impact (blueprint §17.5 α-objective, TRD §20)."""

from engine.models.context import ConstraintContext
from engine.constraints.base import ConstraintRule
from engine.constraints.types import ConstraintType
from engine.constraints.severity import ConstraintSeverity
from engine.constraints._toolkit import evidence, make_result


class TrainImpactRule(ConstraintRule):
    """Blocks should minimize proximity to scheduled train movements.

    SOFT: overlapping train movements on the block's section are a HARD
    failure (RAILMIND.HARD.TRAIN_PATH_CONFLICT); this rule warns about the
    *near misses* — trains on the block's section passing within the configured
    buffer of the block interval — and, when no train touches the section,
    reports the count as a low-impact PASS.
    """

    rule_id = "RAILMIND.SOFT.TRAIN_IMPACT"
    rule_version = "1.0.0"
    name = "Minimize train impact"
    description = (
        "Blocks should keep a temporal buffer from scheduled train movements "
        "on the same section (configurable buffer minutes)."
    )
    constraint_type = ConstraintType.SOFT

    def evaluate(self, context: ConstraintContext):
        block = context.candidate_block
        section_id = block.section_id
        buffer = context.configuration.train_impact_buffer_minutes

        near_misses = []  # (train_id, gap_minutes, start, end)
        for path in context.train_paths:
            for segment in path.segments:
                if segment.section_id != section_id:
                    continue
                # Gap = 0 only if strict overlap — that is a hard failure, not
                # this rule's concern.
                latest_start = max(block.interval.start, segment.interval.start)
                earliest_end = min(block.interval.end, segment.interval.end)
                if latest_start < earliest_end:
                    continue  # strict overlap → hard rule handles it
                gap = min(
                    abs((segment.interval.start - block.interval.end).total_seconds()),
                    abs((block.interval.start - segment.interval.end).total_seconds()),
                ) / 60.0
                if gap <= buffer:
                    near_misses.append((path.train_id, gap, segment.interval.start, segment.interval.end))

        near_misses.sort(key=lambda n: (n[1], n[0]))
        ev = [
            evidence("configuration", "Train-impact buffer (minutes)", buffer),
        ]
        entities = [f"section:{section_id}"]

        if not near_misses:
            checked = sum(
                1 for p in context.train_paths for s in p.segments if s.section_id == section_id
            )
            ev.append(evidence("context", "Train segments on section (no near miss)", float(checked)))
            return make_result(
                self,
                "PASS",
                ConstraintSeverity.INFO,
                "No trains near the block",
                (
                    f"No scheduled train on section {section_id} passes within "
                    f"{buffer:.0f} minutes of the block interval."
                ),
                ev,
                entities,
            )

        ev.extend(
            evidence(
                f"train:{train_id}",
                f"Passes {gap:.1f} min from the block (segment {start.isoformat()} → {end.isoformat()})",
                gap,
            )
            for train_id, gap, start, end in near_misses
        )
        worst = near_misses[0]
        return make_result(
            self,
            "WARNING",
            ConstraintSeverity.WARNING,
            "Train passes close to block",
            (
                f"{len(near_misses)} scheduled train(s) on section {section_id} "
                f"pass within the {buffer:.0f}-minute buffer; closest is "
                f"{worst[0]} at {worst[1]:.1f} minutes."
            ),
            ev,
            entities + [f"train:{n[0]}" for n in near_misses],
            violation_degree=buffer - worst[1] if buffer > 0 else 0.0,
        )
